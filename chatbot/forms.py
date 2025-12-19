from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from chat.models import Conversation, UserMessage


class UserSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Conversation title (optional)'}),
        }


class UserMessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter message...'}),
        }
