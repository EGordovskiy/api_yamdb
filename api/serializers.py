from rest_framework import serializers
from .models import Category, Genre, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'email', 'first_name', 'last_name', 'bio')


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)



class CategorySerializer(serializers.Serializer):
    class Meta:
        fields = '__all__'
        model = Category


class GenreSerializer(serializers.Serializer):
    class Meta:
        fields = '__all__'
        model = Genre

class TitleSerializer(serializers.Serializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title