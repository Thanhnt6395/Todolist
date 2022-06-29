from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from renderer.custom_renderer import CustomRenderer
from .serializers import RegisterSerializers, UserSerializers


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
