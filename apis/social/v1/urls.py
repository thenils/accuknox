from django.urls import path
from rest_framework.routers import DefaultRouter

from apis.social.v1.views import SearchUsersView, FriendViewSet

router = DefaultRouter()
router.register("connections", FriendViewSet, basename="connections")

urlpatterns = [
    path("users/", SearchUsersView.as_view(), name="search-users"),
]

urlpatterns += router.urls