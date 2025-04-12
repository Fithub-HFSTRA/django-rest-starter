"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import create_prompt, get_modified_prompt

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication endpoints
    # Protected endpoint
    path('api/me/', MeAPIView.as_view(), name='me'),
    path('api/prompt/', create_prompt, name='create_prompt'),
    path('api/top_prompt/', get_modified_prompt, name='get_modified_prompt'),
]

