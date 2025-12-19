from .forms import UserSignUpForm
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.urls import reverse

from chat.models import Conversation, UserMessage, AssistantMessage
from chat.ollama import build_context, chat_with_ollama
from .forms import ConversationForm, UserMessageForm


class SignUpView(View):
    def get(self, request):
        form = UserSignUpForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after sign-up
            # Redirect to conversations list after successful sign-up
            return redirect('conversations')
        return render(request, 'registration/signup.html', {'form': form})


@login_required
def conversations_list(request):
    user = request.user
    conversations = Conversation.objects.filter(
        user=user).order_by('-created_at')

    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conv = form.save(commit=False)
            conv.user = user
            conv.save()
            if not conv.title:
                conv.title = f"Conversation {conv.id}"
                conv.save()
            return redirect('conversation_detail', pk=conv.id)
    else:
        form = ConversationForm()

    return render(request, 'chatbot/conversations.html', {
        'conversations': conversations,
        'form': form,
    })


@login_required
def conversation_detail(request, pk):
    conv = get_object_or_404(Conversation, id=pk, user=request.user)
    messages = conv.user_messages.order_by('created_at')

    # create message
    if request.method == 'POST' and 'create_message' in request.POST:
        msg_form = UserMessageForm(request.POST)
        if msg_form.is_valid():
            user_msg = msg_form.save(commit=False)
            user_msg.conversation = conv
            user_msg.save()

            # generate assistant reply
            context = build_context(conv)
            reply = chat_with_ollama(context)
            AssistantMessage.objects.create(
                user_message=user_msg, content=reply)
            return redirect('conversation_detail', pk=pk)
    else:
        msg_form = UserMessageForm()

    # conversation title edit
    conv_form = ConversationForm(instance=conv)

    return render(request, 'chatbot/conversation_detail.html', {
        'conversation': conv,
        'messages': messages,
        'msg_form': msg_form,
        'conv_form': conv_form,
    })


@login_required
def conversation_edit(request, pk):
    conv = get_object_or_404(Conversation, id=pk, user=request.user)
    if request.method == 'POST':
        form = ConversationForm(request.POST, instance=conv)
        if form.is_valid():
            form.save()
            return redirect('conversations')
    return redirect('conversations')


@login_required
def conversation_delete(request, pk):
    conv = get_object_or_404(Conversation, id=pk, user=request.user)
    if request.method == 'POST':
        conv.delete()
    return redirect('conversations')


@login_required
def message_edit(request, conversation_id, message_id):
    conv = get_object_or_404(
        Conversation, id=conversation_id, user=request.user)
    user_msg = get_object_or_404(UserMessage, id=message_id, conversation=conv)

    if request.method == 'POST':
        form = UserMessageForm(request.POST, instance=user_msg)
        if form.is_valid():
            form.save()
            # regenerate assistant reply for this message
            context = build_context(conv)
            reply = chat_with_ollama(context)
            try:
                assistant = user_msg.assistant_reply
                assistant.content = reply
                assistant.save()
            except AssistantMessage.DoesNotExist:
                AssistantMessage.objects.create(
                    user_message=user_msg, content=reply)
            return redirect('conversation_detail', pk=conversation_id)
    else:
        form = UserMessageForm(instance=user_msg)
    return render(request, 'chatbot/message_edit.html', {'form': form, 'conversation': conv, 'message': user_msg})


@login_required
def message_delete(request, conversation_id, message_id):
    conv = get_object_or_404(
        Conversation, id=conversation_id, user=request.user)
    user_msg = get_object_or_404(UserMessage, id=message_id, conversation=conv)
    if request.method == 'POST':
        user_msg.delete()
    return redirect('conversation_detail', pk=conversation_id)
