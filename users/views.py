from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import api_view

from .serializers import RegisterSerializer, UserSerializer 

# @api_view(["GET"])
# def test(request):
#   return Response("Hello, World!")

class RegisterView(APIView):

  def post(self, request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

