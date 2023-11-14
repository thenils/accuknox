from django.urls import path, include

urlpatterns = [
    path('auth/', include('apis.auth.urls')),
    path('social/', include('apis.social.urls')),

]