"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path("api/v1/friends/", include("friends.urls")),
    path("api/v1/messages/", include("direct_messages.urls")),
    path("api/v1/notices/", include("notices.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/pets/", include("pets.urls")),
    path("api/v1/posts/", include("posts.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/weathers/", include("weathers.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
