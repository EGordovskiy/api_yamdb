from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    get_confirmation_code,
    get_jwt_token,
    GenreViewSet, 
    CategoryViewSet, 
    TitleViewSet
    )

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('genres', GenreViewSet)
router.register('category', CategoryViewSet)
router.register('title', TitleViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/email/', get_confirmation_code),
    path('auth/token/', get_jwt_token),
]