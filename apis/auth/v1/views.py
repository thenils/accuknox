from django.contrib.auth import user_logged_out
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apis.auth.v1.serializer import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        response.data['message'] = 'user registered successfully. please login to continue'

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if "refresh_token" not in data:
            return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)

        # Manually emit the user_logged_out signal to log out the user
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

        # Blacklist the refresh token using Django's blacklist app
        token.blacklist()

        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
