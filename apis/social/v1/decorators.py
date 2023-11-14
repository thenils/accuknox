from functools import wraps

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from apps.social.models import FriendRequest


def limit_requests_per_minute(request_limit):
    """
    decorator that allow to maintain request limit in a single minute
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            print(f"User: {request.user}")
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

            user = request.user.is_
            print(user)

            start_of_minute = timezone.now().replace(second=0, microsecond=0)
            sent_requests_count = FriendRequest.objects.filter(user=user, created_at__gte=start_of_minute).count()

            if sent_requests_count >= request_limit:
                return Response({'error': 'Exceeded the request limit.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

def check_limit(user, limit):
    start_of_minute = timezone.now().replace(second=0, microsecond=0)
    sent_requests_count = FriendRequest.objects.filter(user=user, created_at__gte=start_of_minute).count()

    if sent_requests_count >= limit:
        return Response({'error': 'Exceeded the request limit.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
