from rest_framework import serializers
from .models import Conversation, UserMessage, AssistantMessage


class AssistantMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMessage
        fields = ['id', 'content', 'created_at']


class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMessage
        fields = ['id', 'content', 'created_at']


class MessagePairSerializer(serializers.ModelSerializer):
    assistant = serializers.SerializerMethodField()

    class Meta:
        model = UserMessage
        fields = ['id', 'content', 'created_at', 'assistant']

    def get_assistant(self, obj):
        assistant = getattr(obj, 'assistant_reply', None)
        if assistant:
            return AssistantMessageSerializer(assistant).data
        return None


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last_user = obj.user_messages.order_by('-created_at').first()
        if not last_user:
            return None
        assistant = getattr(last_user, 'assistant_reply', None)
        return assistant.content if assistant else last_user.content


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    conversation_id = serializers.IntegerField(required=False)
