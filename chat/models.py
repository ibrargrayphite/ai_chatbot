from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"{self.user.username} - {self.id}"


class UserMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        related_name='user_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UserMessage {self.id} ({self.conversation_id})"


class AssistantMessage(models.Model):
    # one-to-one reply for a specific user message
    user_message = models.OneToOneField(
        UserMessage,
        related_name='assistant_reply',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AssistantMessage {self.id} -> UserMessage {self.user_message_id}"
