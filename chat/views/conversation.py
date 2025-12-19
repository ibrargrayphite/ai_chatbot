from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Conversation, UserMessage, AssistantMessage
from chat.serializers import (
    ConversationSerializer,
    MessagePairSerializer,
    ChatRequestSerializer
)
from chat.ollama import build_context, chat_with_ollama, generate_title_from_conversation


class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # create conversation, then if no title provided auto-generate one
        conversation = serializer.save(user=self.request.user)
        if not conversation.title:
            conversation.title = f"New Chat"
            conversation.save()


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_serializer_class(self):
        if getattr(self, 'request', None) and self.request.method == 'POST':
            return ChatRequestSerializer
        return ConversationSerializer

    def get_object(self, pk, user):
        return Conversation.objects.filter(id=pk, user=user).first()

    def get(self, request, pk):
        """List all messages in the conversation."""
        conversation = self.get_object(pk, request.user)
        if not conversation:
            return Response(status=status.HTTP_404_NOT_FOUND)

        msgs = conversation.user_messages.order_by('created_at')
        serializer = MessagePairSerializer(msgs, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update conversation title only."""
        conversation = self.get_object(pk, request.user)
        if not conversation:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ConversationSerializer(
            conversation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Only allow title to be updated
        title = serializer.validated_data.get('title')
        if title is not None:
            conversation.title = title
            conversation.save()
        return Response(ConversationSerializer(conversation).data)

    def delete(self, request, pk):
        conversation = self.get_object(pk, request.user)
        if not conversation:
            return Response(status=status.HTTP_404_NOT_FOUND)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        """Add new user message to conversation and get AI response."""
        conversation = self.get_object(pk, request.user)
        if not conversation:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]

        # create user message
        user_msg = UserMessage.objects.create(
            conversation=conversation,
            content=message
        )

        # build context and get reply
        context = build_context(conversation)
        reply = chat_with_ollama(context)

        AssistantMessage.objects.create(
            user_message=user_msg,
            content=reply
        )

        try:
            msg_count = conversation.user_messages.count()
        except Exception:
            msg_count = None

        if (msg_count == 1) and (not conversation.title or conversation.title.startswith("New Chat") or conversation.title.strip() == ""):
            new_title = generate_title_from_conversation(reply)
            if new_title:
                conversation.title = new_title
                conversation.save()

        return Response({"reply": reply, "user_message_id": user_msg.id}, status=status.HTTP_201_CREATED)
