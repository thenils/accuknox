from django.urls import path, include

urlpatterns = [
    path('v1/', include('apis.auth.v1.urls'))
]