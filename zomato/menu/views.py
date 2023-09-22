from django.http import JsonResponse
from django.contrib import messages, auth
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import User as CustomUser
import json
import os



@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if a user with the same username already exists
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        if password == confirm_password:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                confirm_password=confirm_password
            )
            user.save()
            return JsonResponse({'message': 'User registered successfully.'}, status=201)
        else:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        try:
            user = CustomUser.objects.get(username=username)
            if user.password == password:
                # Authentication successful
                auth_login(request, user)
                print(user.username)
                messages.success(request, 'Logged in successfully.')
                return JsonResponse({'message': 'Logged in successfully.','username': user.username}, status=200)
            else:
                return JsonResponse({'error': 'Invalid password for the provided username.'}, status=400)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
def menu(request):
    data = {"message": "hello"}
    return JsonResponse(data)