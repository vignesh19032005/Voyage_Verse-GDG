from django.shortcuts import render,redirect
from .utils import get_budget_considerations, initialize_model, get_model_response, get_group_size_considerations, get_custom_places, get_dietary_considerations, save_itinerary, get_place_time
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import datetime

def home(request):
    return render(request,'index.html')

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([first_name, last_name, email, phone_number, password, confirm_password]):
            messages.error(request, 'All fields are required')
            return render(request, 'signup.html')
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'signup.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'signup.html')
            
        try:
            # Create user
            user = User.objects.create_user(
                username=email,  # Using email as username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Update phone number
            user.userprofile.phone_number = phone_number
            user.userprofile.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
            
        except Exception as e:
            # messages.error(request, f'Error creating user: {str(e)}')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')
    
def login(request):
    if request.user.is_authenticated:
        return redirect('demo')
        
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password1')

        if not all([email, password]):
            messages.error(request, "Please provide both email and password")
            return render(request, "login.html")

        try:
            user = authenticate(username=email, password=password)
            if user is not None:
                auth_login(request, user)
                # Get the next parameter or default to 'demo'
                next_page = request.GET.get('next', 'demo')
                return redirect(next_page)
            else:
                messages.error(request, "Invalid email or password")
        except Exception as e:
            messages.error(request, "An error occurred during login")
            # Log the error here for debugging
            print(f"Error in login: {str(e)}")

    return render(request, "login.html")

def generate_itinerary(request):
    if request.method == 'POST':
        # Retrieve input from form
        destination = request.POST.get('destination')
        days = int(request.POST.get('days'))
        budget = request.POST.get('budget')
        preferred_places = request.POST.get('preferred_places', '').split(',')
        dietary_preference = request.POST.get('dietary_preference')
        number_of_persons = int(request.POST.get('number_of_persons'))
        
        # Get the list of travel types from the form
        travel_types = request.POST.getlist('travel_types')
        
        # Clean up preferred places if multiple are provided
        preferred_places = [place.strip() for place in preferred_places if place]

        # Generate itinerary using the function in utils.py
        try:
            itinerary_text = get_model_response(
                places_data={},  # Placeholder for actual places data, if any
                place_name=destination,
                days=days,
                travel_types=travel_types,
                group_size=number_of_persons,
                dietary_preference=dietary_preference,
                budget_preference=budget,
                custom_places=preferred_places
            )

            # Pass itinerary details to the template for rendering
            itinerary = {
                'destination': destination,
                'details': itinerary_text
            }
            return render(request, 'demo.html', {'itinerary': itinerary})

        except Exception as e:
            # Handle errors and show error message in template
            error_message = f"An error occurred: {str(e)}"
            return render(request, 'demo.html', {'error': error_message})

    # If not a POST request, render the form in demo.html
    return render(request, 'demo.html')


def demo(request):
    return render(request, 'demo.html')


def itinerary(request):
    return render(request, 'itinerary.html')

def logout_view(request):  # Renamed function
    auth.logout(request)   # Use auth.logout instead
    messages.success(request, "Successfully logged out")
    return redirect('index')  # Better to use named URL

def pondicherry(request):
    return render(request, 'pondicherry.html')
def kullu(request):
    return render(request, 'kullu.html')
def goa(request):
    return render(request, 'goa.html')
def andamanislands(request):
    return render(request, 'andamanislands.html')
def agra(request):
    return render(request, 'agra.html')
def amristar(request):
    return render(request, 'amristar.html')

from django.http import JsonResponse
from .utils import travel_chatbot
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input')
            chatbot_response = travel_chatbot(user_input)
            return JsonResponse({'chatbot_response': chatbot_response})
        except Exception as e:
            print(f"Error in chat_response view: {str(e)}")
            return JsonResponse({'chatbot_response': 'Sorry, there was an error processing your request.'}, status=500)

    return render(request, 'demo.html')
