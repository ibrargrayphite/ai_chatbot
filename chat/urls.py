from django.urls import path
from .views.conversation import (
    ConversationListCreateView,
    ConversationDetailView
)
from .views.message import (
    MessageListView,
    MessageDetailView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # path("chat/", chat_view),

    path("conversations/", ConversationListCreateView.as_view()),
    path("conversations/<int:pk>/", ConversationDetailView.as_view()),

    path(
        "conversations/<int:conversation_id>/messages/",
        MessageListView.as_view()
    ),
    path(
        "conversations/<int:conversation_id>/messages/<int:pk>/",
        MessageDetailView.as_view()
    ),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
