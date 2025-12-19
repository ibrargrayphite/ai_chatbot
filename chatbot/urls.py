from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('', views.conversations_list, name='conversations'),
    path('conversations/', views.conversations_list, name='conversations'),
    path('conversations/<int:pk>/', views.conversation_detail,
         name='conversation_detail'),
    path('conversations/<int:pk>/edit/',
         views.conversation_edit, name='conversation_edit'),
    path('conversations/<int:pk>/delete/',
         views.conversation_delete, name='conversation_delete'),

    path('conversations/<int:conversation_id>/messages/<int:message_id>/edit/',
         views.message_edit, name='message_edit'),
    path('conversations/<int:conversation_id>/messages/<int:message_id>/delete/',
         views.message_delete, name='message_delete'),
]
