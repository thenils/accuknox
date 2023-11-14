from django.urls import path, include

urlpatterns = [
    path('v1/', include('apis.social.v1.urls'))
]