# views.py
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from functools import wraps
import json
import time



import google.generativeai as genai
from groq import Groq

import os

# Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Configure APIs
genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)



class ModelManager:
    def __init__(self):
        self.current_model = "gemini"
        self.last_error_time = 0
        self.error_cooldown = 500  # 5 minutes cooldown before retrying failed model

    def switch_model(self):
        if self.current_model == "gemini":
            self.current_model = "groq"
        else:
            self.current_model = "gemini"
        self.last_error_time = time.time()

model_manager = ModelManager()

def handle_rate_limits(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # If enough time has passed since last error, try switching back to primary model
            if time.time() - model_manager.last_error_time > model_manager.error_cooldown:
                model_manager.current_model = "gemini"
            
            # Switch model and retry
            model_manager.switch_model()
            return func(*args, **kwargs)
    return wrapper

def review_with_gemini(code):
    model = genai.GenerativeModel(
        # model_name='models/gemini-1.5-pro-latest',
        model_name='models/gemini-1.5-flash',

        system_instruction="""You are a fashion suggestion system that helps users find outfits based on their preferences, body type, and current trends. 
        The system provides personalized fashion recommendations based on their favorite styles, colors, body measurements, and clothing items.
        Your task is to analyze these inputs and suggest suitable outfits for different occasions, ensuring they look fashionable and feel confident.
        Please generate outfit suggestions based on the user’s preferences and lifestyle inputs.make it point by point and only just say the needed clothes for a outfit . dont use * """
        #                 """
    )


    
    try:
        response = model.generate_content(code)
        print(f"Gemini response: {response.text}")  # Log the response text for debugging
        return response.text.strip()
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")  # Log the error from Gemini API
        raise  # Re-raise the exception after logging it

def review_with_groq(code):
    system_prompt = """You are a fashion suggestion system that helps users find outfits based on their preferences, body type, and current trends. 
        The system provides personalized fashion recommendations based on their favorite styles, colors, body measurements, and clothing items.
        Your task is to analyze these inputs and suggest suitable outfits for different occasions, ensuring they look fashionable and feel confident.
        Please generate outfit suggestions based on the user’s preferences and lifestyle inputs.make it point by point and only just say the needed clothes for a outfit"""
    
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": code}
        ],
        model="llama3-70b-8192",
        temperature=0.7,
        max_tokens=1000
    )
    return chat_completion.choices[0].message.content.strip()




def home(request):
    return render(request, 'premade/home.html')





    


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import PlagarismChat, UserQueryCount, CustomUser
from .forms import CustomUserCreationForm, LoginForm
from django.db.models import Sum
from django.utils import timezone

def is_owner(user):
    return user.is_owner

def login_view(request):
    # If the user is already authenticated, redirect to the appropriate dashboard
    if request.user.is_authenticated:
        # Redirect to owner dashboard if user is owner
        if request.user.is_owner:
            return redirect('owner_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to owner dashboard if user is owner
                if user.is_owner:
                    return redirect('owner_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def check_query_limit(user):
    """
    Check if user has reached their monthly query limit
    """
    current_month = timezone.now().date().replace(day=1)
    query_count = UserQueryCount.objects.filter(
        user=user,
        month=current_month
    ).first()
    
    if query_count:
        total_queries = (query_count.live_queries + 
                        query_count.chat_queries + 
                        query_count.file_queries)
        return total_queries < user.query_limit
    return True


@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
    # Get current month's statistics
    current_month = timezone.now().date().replace(day=1)
    
    # Get all users and their query counts
    users = CustomUser.objects.filter(is_owner=False)
    user_stats = []
    
    for user in users:
        query_count = UserQueryCount.objects.filter(
            user=user,
            month=current_month
        ).first()
        
        if query_count:
            user_stats.append({
                'username': user.username,
                'live_queries': query_count.live_queries,
                'chat_queries': query_count.chat_queries,
                'file_queries': query_count.file_queries,
                'total_queries': (query_count.live_queries + 
                                query_count.chat_queries + 
                                query_count.file_queries),
                'query_limit': user.query_limit
            })
        else:
            user_stats.append({
                'username': user.username,
                'live_queries': 0,
                'chat_queries': 0,
                'file_queries': 0,
                'total_queries': 0,
                'query_limit': user.query_limit
            })
    
    context = {
        'user_stats': user_stats,
        'current_month': current_month
    }
    
    return render(request, 'owner_dashboard.html', context)

from django.shortcuts import get_object_or_404

@login_required
def delete_user(request, username):
    # Ensure the logged-in user is an owner
    if not request.user.is_owner:
        messages.error(request, "You do not have permission to delete users.")
        return redirect('owner_dashboard')  # Redirect to the owner dashboard
    
    user_to_delete = get_object_or_404(CustomUser, username=username)

    # Prevent owners from deleting themselves
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('owner_dashboard')

    # Perform deletion
    user_to_delete.delete()
    messages.success(request, f"User {user_to_delete.username} has been deleted.")
    return redirect('owner_dashboard')  # Redirect to the owner dashboard


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def review_code_live(request):
    if not check_query_limit(request.user):
        return JsonResponse({"error": "Monthly query limit reached"}, status=403)
        
    try:
        data = json.loads(request.body)
        code_input = data.get("code_input")
        
        if model_manager.current_model == "gemini":
            review = review_with_gemini(code_input)
        else:
            review = review_with_groq(code_input)
        
        # Record the query
        UserQueryCount.increment_query(request.user, 'live')
        
        return JsonResponse({
            "review": review,
            "model_used": model_manager.current_model
        })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "model_used": model_manager.current_model
        }, status=500)

@login_required
def review_code_chat(request):
    if not check_query_limit(request.user):
        return JsonResponse({"error": "Monthly query limit reached"}, status=403)

    if request.method == 'POST':
        try:
            code_input = request.POST.get('code_input')
            print(code_input)
            if model_manager.current_model == "gemini":
                review = review_with_gemini(code_input)
            else:
                review = review_with_groq(code_input)
                
            chat = PlagarismChat.objects.create(
                user=request.user,
                code=code_input,
                review=review,
                model_used=model_manager.current_model,
                review_type='chat'
            )
            
            UserQueryCount.increment_query(request.user, 'chat')

            # return JsonResponse({
            #     "review": review,
            #     "chat_id": chat.id,
            #     "model_used": model_manager.current_model
            # })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    chats = PlagarismChat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat.html', {'chats': chats})



@login_required
def review_file(request):
    if not check_query_limit(request.user):
        return JsonResponse({"error": "Monthly query limit reached"}, status=403)

    if request.method == 'GET':
        # Get chats from last 12 hours
        twelve_hours_ago = timezone.now() - timedelta(hours=12)
        chat_history = PlagarismChat.objects.filter(
            user=request.user,
            created_at__gte=twelve_hours_ago
        ).order_by('created_at')
        
        return render(request, 'chat.html', {
            'chat_history': chat_history
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            code_content = data.get('code_content')
            
            if not code_content:
                return JsonResponse({"error": "Please provide some code"}, status=400)

            # Review the code using the appropriate model
            if model_manager.current_model == "gemini":
                review = review_with_gemini(code_content)
            else:
                review = review_with_groq(code_content)

            # Create a chat record
            chat = PlagarismChat.objects.create(
                user=request.user,
                code=code_content,
                review=review,
                model_used=model_manager.current_model,
                review_type='chat'
            )
            suggestion_points = [point.strip() for point in review.split('*') if point]

            UserQueryCount.increment_query(request.user, 'chat')
            print(suggestion_points)
            return JsonResponse({
                "career_suggestion": suggestion_points
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


def home(request):
    return render(request, 'premade/home.html')

@login_required
def live(request):
    return render(request, 'active.html')



# views.py
import os
from PIL import Image
import numpy as np
import pickle
import tensorflow
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.layers import GlobalMaxPooling2D
import cv2
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Update these paths to your project directory
IMAGES_DIR = os.path.join(settings.BASE_DIR, 'New folder', 'image')
FEATURE_LIST_PATH = os.path.join(settings.BASE_DIR, 'featurevector.pkl')
FILENAMES_PATH = os.path.join(settings.BASE_DIR, 'filenames.pkl')

# Load precomputed features and filenames
feature_list = np.array(pickle.load(open(FEATURE_LIST_PATH, 'rb')))
filenames = pickle.load(open(FILENAMES_PATH, 'rb'))

# Load ResNet50 model
model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
model.trainable = False
model = tensorflow.keras.Sequential([
    model,
    GlobalMaxPooling2D()
])

def serve_image(image_path):
    """
    Serve image directly from the file system
    """
    try:
        with open(image_path, 'rb') as img_file:
            return img_file.read()
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def extract_feature(img_path, model):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224))
    img = np.array(img)
    expand_img = np.expand_dims(img, axis=0)
    pre_image = preprocess_input(expand_img)
    result = model.predict(pre_image).flatten()
    normalized = result / norm(result)
    return normalized

def recommend(features, feature_list):
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)
    distance, indices = neighbors.kneighbors([features])
    return indices

def fashion_recommend(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        
        # Save the uploaded file
        filename = fs.save(f'uploads/{uploaded_file.name}', uploaded_file)
        uploaded_file_path = fs.path(filename)
        
        # Extract features and get recommendations
        features = extract_feature(uploaded_file_path, model)
        indices = recommend(features, feature_list)
        
        # Use actual file paths for recommended images
        recommended_images = []
        for idx in indices[0]:
            # Get the filename from the full path
            img_filename = os.path.basename(filenames[idx])
            recommended_images.append(img_filename)
        
        context = {
            'uploaded_image': f'/media/uploads/{uploaded_file.name}',
            'recommended_images': recommended_images
        }
        UserQueryCount.increment_query(request.user, 'file')

        return render(request, 'fashion/results.html', context)
    
    return render(request, 'fashion/upload.html')

def serve_fashion_image(request, image_name):
    """View to serve fashion images directly"""
    image_path = os.path.join(IMAGES_DIR, image_name)
    image_data = serve_image(image_path)

    if image_data:
        from django.http import HttpResponse
        return HttpResponse(image_data, content_type='image/jpeg')
    return HttpResponse(status=404)