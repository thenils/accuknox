from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apis.auth.v1.serializer import CustomJWTSerializer
from apis.auth.v1.views import RegisterView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register-user'),
    path('login/', TokenObtainPairView.as_view(serializer_class=CustomJWTSerializer), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]