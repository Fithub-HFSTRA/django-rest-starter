# views.py (create this file in your main directory)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import serializers
from django.db.models import Sum
from .models import UserPrompt
from openai import OpenAI
import os

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def options(self, request, *args, **kwargs):
        response = Response()
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                response = Response({
                    'user': UserSerializer(user).data,
                    'message': 'Login successful'
                })
                response["Access-Control-Allow-Origin"] = "http://localhost:3000"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class CreatePromptView(APIView):
    """
    Accepts a POST request with JSON payload containing:
      - user_id: The user identifier.
      - prompt: The text prompt.
      - watch_time: An integer representing the watch time.
    Saves the record into the database.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        prompt_text = request.data.get('prompt')
        watch_time = request.data.get('watch_time')

        if not (user_id and prompt_text and watch_time is not None):
            return Response(
                {'error': 'Missing required fields: user_id, prompt, and watch_time are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            entry = UserPrompt(user_id=user_id, prompt=prompt_text, watch_time=watch_time)
            entry.save()
            return Response({'message': 'Prompt saved successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TopPromptView(APIView):
    """
    Accepts a GET request to:
      - Aggregate total watch_time per user.
      - Find the user with the highest cumulative watch time.
      - Retrieve the latest prompt from that user.
      - Modify the prompt using a simple placeholder custom function.
      - Return the top user information along with the modified prompt.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Aggregate total watch time per user and sort descending
        aggregated = UserPrompt.objects.values('user_id') \
            .annotate(total_watch_time=Sum('watch_time')) \
            .order_by('-total_watch_time')

        if not aggregated:
            return Response({'error': 'No prompt data available.'}, status=status.HTTP_404_NOT_FOUND)

        # Determine the user with the highest cumulative watch time
        top_user_id = aggregated[0]['user_id']
        total_watch_time = aggregated[0]['total_watch_time']

        # Retrieve the most recent prompt for this top user
        latest_entry = UserPrompt.objects.filter(user_id=top_user_id).order_by('-timestamp').first()
        if not latest_entry:
            return Response({'error': 'No prompt found for the top user.'}, status=status.HTTP_404_NOT_FOUND)

        # Placeholder custom function: Simply prepend "Modified: " to the original prompt
        modified_prompt = "Modified: " + latest_entry.prompt

        response_data = {
            'top_user': top_user_id,
            'total_watch_time': total_watch_time,
            'modified_prompt': modified_prompt
        }
        return Response(response_data, status=status.HTTP_200_OK)
