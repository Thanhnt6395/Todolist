import json
from datetime import timedelta

import jwt
import redis
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from Todolist import settings
from renderer.custom_renderer import CustomRenderer
from .models import CustomUser
from .serializers import RegisterSerializers, UserSerializers, ActivateCallBackSerializer, LoginSerializer


class RegisterUserView(generics.GenericAPIView):
    serializer_class = RegisterSerializers
    permission_classes = [AllowAny]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        data = request.data
        serializer = RegisterSerializers(data=data)
        serializer.is_valid(raise_exception=True)
        user, tokens = serializer.save()

        response = {
            'user': UserSerializers(user, context=self.get_serializer_context()).data,
            'refresh': tokens.get('refresh'),
            'access': tokens.get('access')
        }
        return Response(data={'data': response}, status=status.HTTP_201_CREATED)


class ActivateCallBackView(generics.GenericAPIView):
    serializer_class = ActivateCallBackSerializer
    permission_classes = [AllowAny]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        token = request.query_params.get('token', None)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = CustomUser.objects.get(pk=payload['user_id'])
            user.is_verified = True
            user.save()
            return Response(data={'data': None}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as e:
            return Response({'error': 'Token Active expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError as e:
            return Response({'error': 'token is missing'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get('id')
        tokens = serializer.validated_data.get('tokens')

        rd = redis.Redis(host="localhost")
        json_logged = json.dumps({
            "access_token": tokens.get('access')
        })
        rd.mset({str(user_id): json_logged})
        rd.expire(str(user_id), time=timedelta(days=1))
        response = {
            'message': 'You are logging',
            'data': json.dumps({
                'user_id': str(user_id),
                'tokens': tokens
            })
        }
        return Response(data=response, status=status.HTTP_200_OK)
