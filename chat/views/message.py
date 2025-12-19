from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import UserMessage, AssistantMessage
from chat.serializers import UserMessageSerializer, MessagePairSerializer
from chat.ollama import build_context, chat_with_ollama


class MessageListView(generics.ListAPIView):
    serializer_class = MessagePairSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMessage.objects.filter(
            conversation__id=self.kwargs['conversation_id'],
            conversation__user=self.request.user
        ).order_by('created_at')


class MessageDetailView(generics.DestroyAPIView, generics.UpdateAPIView):
    serializer_class = UserMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMessage.objects.filter(
            conversation__user=self.request.user
        )

    def update(self, request, *args, **kwargs):
        # Update a user message and regenerate/update the assistant reply
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # regenerate assistant reply for the conversation context
        conversation = instance.conversation
        context = build_context(conversation)
        reply = chat_with_ollama(context)

        # update existing assistant reply or create new one linked to this user message
        try:
            assistant = instance.assistant_reply
            assistant.content = reply
            assistant.save()
        except AssistantMessage.DoesNotExist:
            AssistantMessage.objects.create(
                user_message=instance, content=reply)

        return Response({"reply": reply}, status=status.HTTP_200_OK)
