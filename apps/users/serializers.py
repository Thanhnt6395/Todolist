from django.core.mail import EmailMessage

from rest_framework import serializers
from rest_framework.exceptions import NotFound, AuthenticationFailed, APIException

from Todolist.settings import db_config
from apps.users.models import CustomUser


class UserSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex', required=True)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    date_joined = serializers.DateField(required=False)
    last_login = serializers.DateField(required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'is_staff', 'is_active', 'is_verified', 'date_joined', 'last_login')

    def validate(self, attrs):
        try:
            return CustomUser.objects.get(pk=attrs.get('id'))
        except CustomUser.DoesNotExist as e:
            raise NotFound(f"{e}") from e


class RegisterSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=None, min_length=None, allow_blank=False, required=True)
    password = serializers.CharField(max_length=50, min_length=8, required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'is_staff', 'is_active', 'is_verified', 'date_joined', 'last_login')
        read_only_fields = ('is_staff', 'is_active', 'is_verified', 'date_joined', 'last_login')

    def create(self, validated_data):
        try:
            user = CustomUser()
            user.set_password(validated_data.get('password'))
            user.email = validated_data.get('email')
            user.save()
            tokens = user.tokens()
            try:
                # TODO: Send mail verify
                current_site = db_config['CURRENT_DOMAIN']
                link = f"{current_site}/api/users/verify_email?token={tokens.get('refresh')}"
                subject = "Verify your email"
                body = f"""
                    Hello guys!
                    Please click link below to verify your email:
                    {link}
                    
                    ------------------------------------------------------------------------------------
                    Thank you so much!
                """
                email = EmailMessage(subject, body, to=[user.email], from_email=db_config['EMAIL_HOST_USER'])
                email.send()
            except Exception as e:
                raise APIException("Send mail verify failed") from e
            return user, tokens
        except Exception as e:
            raise APIException(f"{e}") from e

