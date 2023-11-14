from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='this email already associated with user try sign in')]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            'email',
            'password',
            "confirm_password",
        )
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": ["The new password and verify password do not match."]})

        return data

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['username'] = self.generate_username(validated_data['email'].split('@')[0].replace('+', ''))
            user = User.objects.create(
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                username=validated_data['username'],
                email=validated_data['email'],
                is_active=True
            )

            user.set_password(validated_data['password'])
            user.save()
            return user

    @staticmethod
    def generate_username(user_name):
        ln = User.objects.filter(username__icontains=user_name).count()
        return f'{user_name}@{ln + 1}' if ln > 0 else user_name


class CustomJWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {
            'username': '',
            'password': attrs.get("password")
        }

        user_obj = User.objects.filter(email=attrs.get("username")).first() or User.objects.filter(
            username=attrs.get("username")).first()
        if user_obj:
            credentials['username'] = user_obj.username

        return super().validate(credentials)
