from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apis.social.v1.decorators import limit_requests_per_minute
from apis.social.v1.serializers import UserSerializer, SendRequestUserSerializer, FriendRequestSerializer
from apps.social.models import FriendRequest
from utils.pagination import LimitOffsetPagination, get_paginated_response


class SearchUsersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        search_keyword = self.request.query_params.get('query', '')
        if '@' in search_keyword:
            queryset = User.objects.filter(email__iexact=search_keyword)
        else:
            queryset = User.objects.filter(
                Q(first_name__icontains=search_keyword) | Q(last_name__icontains=search_keyword))

        return queryset.exclude(id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=UserSerializer,
            queryset=queryset,
            request=request,
            view=self
        )


class FriendViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = request.user
        friends = user.friend_list.friends.all()

        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=UserSerializer,
            queryset=friends,
            request=request,
            view=self
        )

    @classmethod
    def check_limit(cls, user: User, limit):
        """
        to check that user is not sending many request at once
        """
        start_of_minute = timezone.now() - timedelta(minutes=1)
        sent_requests_count = FriendRequest.objects.filter(user=user, created_at__gte=start_of_minute).count()
        if sent_requests_count > limit:
            return True
        return False

    @action(detail=False, methods=["POST"])
    def send_request(self, request):
        user = request.user
        over_req = self.check_limit(user, 3)
        if over_req:
            return Response({'error': 'Exceeded the request limit.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = SendRequestUserSerializer(data=request.data, context={"user": user})
        if serializer.is_valid():
            request_to = serializer.validated_data["request_to"]
            FriendRequest.objects.create(user=user, requested_to=request_to)
            return Response({"message": "friend request has been sent."})
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @action(detail=False, methods=["GET"])
    def requests(self, request):
        user = request.user
        friend_request = user.requested_to.all()

        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=FriendRequestSerializer,
            queryset=friend_request,
            request=request,
            view=self
        )

    @action(detail=False, methods=["GET"])
    def sent_requests(self, request):
        user = request.user
        friend_request = user.requested_by.all()
        return get_paginated_response(
            pagination_class=LimitOffsetPagination,
            serializer_class=FriendRequestSerializer,
            queryset=friend_request,
            request=request,
            view=self
        )

    @action(detail=True, methods=["PATCH"])
    def accept_request(self, request, pk):
        friend_request = get_object_or_404(FriendRequest, pk=pk)
        if friend_request.requested_to != request.user:
            return Response({"message": "this friend request does not belongs to you"},
                            status=status.HTTP_400_BAD_REQUEST)
        if friend_request.status == "Accepted":
            return Response({"message": "already accepted"}, status=status.HTTP_400_BAD_REQUEST)

        if friend_request.status == "Rejected":
            return Response({"message": "request has been rejected please send request again"},
                            status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = "Accepted"
        friend_request.save()
        return Response({"message": "friend request accepted successfully"})

    @action(detail=True, methods=["PATCH"])
    def reject_request(self, request, pk):
        friend_request = get_object_or_404(FriendRequest, pk=pk)
        if friend_request.requested_to != request.user:
            return Response({"message": "this friend request does not belongs to you"},
                            status=status.HTTP_400_BAD_REQUEST)
        if friend_request.status == "Accepted":
            return Response({"message": "this friend request is accepted. unfriend user to remove from friend list"},
                            status=status.HTTP_400_BAD_REQUEST)

        if friend_request.status == "Rejected":
            return Response({"message": "this request has been rejected already"},
                            status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = "Rejected"
        friend_request.save()
        return Response({"message": "friend request accepted successfully"})
