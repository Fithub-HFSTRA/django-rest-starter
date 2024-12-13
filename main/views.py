# views.py (create this file in your main directory)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import serializers
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

class MeAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get the message from the request data
        message = request.data.get("message")
        if not message:
            return Response(
                {"error": "Message is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set up Hugging Face API client
        client = OpenAI(
            base_url=os.environ["HGLINK"], 
            api_key=os.environ["HGKEY"]  # Replace with your actual API key
        )

        try:
            # Create a chat completion request
            chat_completion = client.chat.completions.create(
                model="tgi",
                messages=[
                    {
                        "role": os.environ["HGKEY"],
                        "content": message
                    }
                ],
                top_p=0.5,
                temperature=0.8,
                max_tokens=500,
                stream=True,
                seed=None,
                frequency_penalty=None,
                presence_penalty=None
            )

            # Fetch the response from Hugging Face API
            hf_response = ""
            for chat_message in chat_completion:
                hf_response += chat_message.choices[0].delta.content

            # Return the response from the Hugging Face API
            return Response({"hf_response": hf_response}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle exceptions and return an error response
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
