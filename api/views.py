from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Genre, Category, Title, User
from .permissions import (
    IsAdminOrSuperUser, ReviewCommentPermissions, PermissionMixin
)
from .serializers import (
    ConfirmationCodeSerializer, UserEmailSerializer, UserSerializer,
    GenreSerializer, CategorySerializer, TitleSerializer,
    # TitleCreateSerializer
)
# from .filters import TitlesFilter


@api_view(['POST'])
@permission_classes([AllowAny])
def get_confirmation_code(request):
    username = request.data.get('username')
    serializer = UserEmailSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.data.get('email')
    if username is not None:
        try:
            User.objects.create_user(username=username, email=email)
        except IntegrityError:
            return Response(
                {'Error': 'The user already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    user = get_object_or_404(User, email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Confirmation code',
        f'Confirmation code: {confirmation_code}',
        'Yamdb.net <norep@yamdb.net>',
        [email], 
        fail_silently=False
    )
    return Response(
        {'OK': f'The confirmation code has sent to {email}'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.data.get('email')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, email=email)

    if default_token_generator.check_token(user, confirmation_code):
        refresh = RefreshToken.for_user(user)
        return Response({'access': refresh.access_token}, status=status.HTTP_200_OK)

    return Response(
        {'confirmation_code': 'Bad confirmation code.'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrSuperUser]
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(role=user.role, partial=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    http_method_names = ['get', 'post', 'head', 'delete']
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrSuperUser
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get', 'post', 'head', 'delete']
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrSuperUser
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrSuperUser
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'year', 'genre', 'category']

