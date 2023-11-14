from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers

from apps.social.models import FriendRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class SendRequestUserSerializer(serializers.Serializer):
    request_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    def validate(self, attrs):
        user = self.context["user"]
        request_to = attrs['request_to']

        if request_to in user.friend_list.friends.all():
            raise serializers.ValidationError({"request_to": ["This user is already in your friend list"]})

        friend_requests = FriendRequest.objects.filter(
            Q(user=user, requested_to=request_to, status="Pending") | Q(user=request_to, requested_to=user,
                                                                        status="Pending"))
        if friend_requests.exists():
            raise serializers.ValidationError({"request_to": ["Friend Request is already exists."]})

        return attrs


class FriendRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    requested_to = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ("id","user", "requested_to", "status", "accepted_date")