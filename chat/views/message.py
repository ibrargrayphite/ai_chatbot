from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import Message, Conversation
from chat.serializers import MessageSerializer
from chat.ollama import build_context, chat_with_ollama


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__id=self.kwargs['conversation_id'],
            conversation__user=self.request.user
        ).order_by('created_at')


class MessageDetailView(generics.DestroyAPIView, generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__user=self.request.user
        )

    def update(self, request, *args, **kwargs):
        # Update message content. If it's a user message, generate new AI reply.
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # If updated message is from user, produce new assistant reply
        if instance.role == 'user':
            conversation = instance.conversation
            context = build_context(conversation)
            reply = chat_with_ollama(context)
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=reply
            )
            return Response({"reply": reply}, status=status.HTTP_200_OK)

        return Response(serializer.data)
