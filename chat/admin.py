from django.contrib import admin
from .models import Conversation, UserMessage, AssistantMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at')
    search_fields = ('title', 'user__username')

    class Meta:
        model = Conversation


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'short_content', 'created_at')
    search_fields = ('conversation__title', 'content')

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    short_content.short_description = 'content'

    class Meta:
        model = UserMessage


@admin.register(AssistantMessage)
class AssistantMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_message', 'short_content', 'created_at')
    search_fields = ('user_message__content', 'content')

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    short_content.short_description = 'content'

    class Meta:
        model = AssistantMessage
