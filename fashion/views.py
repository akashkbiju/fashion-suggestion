# views.py
import os
import sys
import warnings

# Suppress TensorFlow, oneDNN, and library deprecation warnings from terminal
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from functools import wraps
import json
import time

import google.generativeai as genai
from groq import Groq

from .models import PlagarismChat, UserQueryCount, CustomUser
from .forms import CustomUserCreationForm, LoginForm

# Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Configure APIs safely
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Notice: Gemini config warning: {e}")

groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Notice: Groq init warning: {e}")


def get_smart_fallback_fashion_suggestion(prompt):
    """
    Fallback fashion suggestion engine when AI API keys are unavailable, expired, or rate-limited.
    Provides personalized outfit recommendations based on user input keywords.
    """
    lower = prompt.lower()
    
    if any(k in lower for k in ['formal', 'office', 'interview', 'meeting', 'corporate', 'business']):
        return (
            "* Topwear: Crisp tailored slim-fit button-down shirt in sky blue or classic white\n"
            "* Bottomwear: Charcoal grey or navy flat-front dress trousers\n"
            "* Layering: Structured dark navy blazer or lightweight formal suit jacket\n"
            "* Footwear: Tan or dark brown Oxford leather shoes with matching leather belt\n"
            "* Accessories: Minimalist analog watch and subtle silver cufflinks"
        )
    elif any(k in lower for k in ['party', 'night', 'club', 'celebration', 'dinner', 'date']):
        return (
            "* Topwear: Satin or silk-blend open-collar shirt in midnight black or deep burgundy\n"
            "* Bottomwear: Slim-fit black tailored chinos or dark selvedge denim\n"
            "* Layering: Tailored biker leather jacket or textured velvet blazer\n"
            "* Footwear: Chelsea boots in black suede or polished leather\n"
            "* Accessories: Sleek metallic wrist chain and signature warm woody fragrance"
        )
    elif any(k in lower for k in ['winter', 'cold', 'sweater', 'jacket', 'hoodie']):
        return (
            "* Topwear: Merino wool turtleneck or chunky cable-knit sweater in beige or forest green\n"
            "* Layering: Wool blend overcoat or down-quilted puffer jacket in camel or navy\n"
            "* Bottomwear: Straight-leg wool flannel trousers or heavy dark denim\n"
            "* Footwear: Waterproof leather lace-up boots or lug-sole Chelsea boots\n"
            "* Accessories: Ribbed cashmere scarf and neutral beanie"
        )
    elif any(k in lower for k in ['summer', 'hot', 'beach', 'vacation', 'resort']):
        return (
            "* Topwear: Breathable relaxed-fit linen shirt in pastel sage or off-white\n"
            "* Bottomwear: Lightweight cotton-linen drawstring shorts or tapered chinos\n"
            "* Footwear: Slip-on woven espadrilles or minimalist white leather sneakers\n"
            "* Accessories: Polarized tortoiseshell sunglasses and woven Panama straw hat\n"
            "* Accent: Braided leather or beaded wrist accent"
        )
    elif any(k in lower for k in ['gym', 'workout', 'sport', 'athletic', 'running']):
        return (
            "* Topwear: Moisture-wicking athletic compression tee or raglan sports t-shirt\n"
            "* Bottomwear: Breathable lightweight track joggers or 5-inch running shorts\n"
            "* Footwear: High-performance cushioned running sneakers\n"
            "* Accessories: Lightweight sweat-resistant baseball cap and smart fitness tracker\n"
            "* Hydration: Insulated sports bottle"
        )
    else:
        # Default versatile casual/smart-casual style
        return (
            "* Topwear: Premium heavyweight cotton crewneck t-shirt or Cuban collar overshirt in beige/olive\n"
            "* Bottomwear: Slim-straight washed indigo denim jeans or relaxed khaki chinos\n"
            "* Footwear: Classic clean white leather low-top sneakers\n"
            "* Layering: Lightweight denim trucker or casual Harrington jacket\n"
            "* Accessories: Minimalist leather-strap watch and sunglasses"
        )


class ModelManager:
    def __init__(self):
        self.current_model = "gemini"
        self.last_error_time = 0
        self.error_cooldown = 300

    def switch_model(self):
        if self.current_model == "gemini":
            self.current_model = "groq"
        else:
            self.current_model = "gemini"
        self.last_error_time = time.time()

model_manager = ModelManager()


def review_with_gemini(prompt):
    model = genai.GenerativeModel(
        model_name='models/gemini-1.5-flash',
        system_instruction="""You are a fashion suggestion system that helps users find outfits based on their preferences, body type, and current trends. 
The system provides personalized fashion recommendations based on their favorite styles, colors, body measurements, and clothing items.
Your task is to analyze these inputs and suggest suitable outfits for different occasions.
Format your response point by point starting with an asterisk (*) for each clothing piece (e.g. * Topwear: ...)."""
    )
    response = model.generate_content(prompt)
    return response.text.strip()


def review_with_groq(prompt):
    if not groq_client:
        raise ValueError("Groq client not configured")
    
    system_prompt = """You are a fashion suggestion system that helps users find outfits based on their preferences, body type, and current trends. 
The system provides personalized fashion recommendations based on their favorite styles, colors, body measurements, and clothing items.
Format your response point by point starting with an asterisk (*) for each clothing piece."""
    
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="llama3-70b-8192",
        temperature=0.7,
        max_tokens=1000
    )
    return chat_completion.choices[0].message.content.strip()


def get_outfit_recommendation(prompt):
    """
    Unified, fail-safe recommendation generator with multi-tier fallback:
    1. Gemini -> 2. Groq -> 3. Smart local fashion suggestion engine
    """
    # Try primary selected model
    if model_manager.current_model == "gemini":
        try:
            return review_with_gemini(prompt), "gemini"
        except Exception as e:
            print(f"Gemini API notice ({e}), trying Groq fallback...")
            model_manager.switch_model()
            try:
                return review_with_groq(prompt), "groq"
            except Exception as e2:
                print(f"Groq API notice ({e2}), applying smart fallback recommendation...")
                return get_smart_fallback_fashion_suggestion(prompt), "expert-rules"
    else:
        try:
            return review_with_groq(prompt), "groq"
        except Exception as e:
            print(f"Groq API notice ({e}), trying Gemini fallback...")
            model_manager.switch_model()
            try:
                return review_with_gemini(prompt), "gemini"
            except Exception as e2:
                print(f"Gemini API notice ({e2}), applying smart fallback recommendation...")
                return get_smart_fallback_fashion_suggestion(prompt), "expert-rules"


def home(request):
    return render(request, 'premade/home.html')


def is_owner(user):
    return user.is_owner


def login_view(request):
    if request.user.is_authenticated:
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
    current_month = timezone.now().date().replace(day=1)
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


@login_required
def delete_user(request, username):
    if not request.user.is_owner:
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('owner_dashboard')
    
    user_to_delete = get_object_or_404(CustomUser, username=username)

    if user_to_delete == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('owner_dashboard')

    user_to_delete.delete()
    messages.success(request, f'User {user_to_delete.username} has been deleted.')
    return redirect('owner_dashboard')


@login_required
@csrf_exempt
@require_http_methods(['POST'])
def review_code_live(request):
    if not check_query_limit(request.user):
        return JsonResponse({'error': 'Monthly query limit reached'}, status=403)
        
    try:
        data = json.loads(request.body)
        code_input = data.get('code_input', '').strip()
        if not code_input:
            return JsonResponse({'error': 'Please provide fashion preferences'}, status=400)
        
        review, model_used = get_outfit_recommendation(code_input)
        UserQueryCount.increment_query(request.user, 'live')
        
        return JsonResponse({
            'review': review,
            'model_used': model_used
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def review_code_chat(request):
    if not check_query_limit(request.user):
        return JsonResponse({'error': 'Monthly query limit reached'}, status=403)

    if request.method == 'POST':
        try:
            code_input = request.POST.get('code_input', '').strip()
            if code_input:
                review, model_used = get_outfit_recommendation(code_input)
                
                PlagarismChat.objects.create(
                    user=request.user,
                    code=code_input,
                    review=review,
                    model_used=model_used,
                    review_type='chat'
                )
                UserQueryCount.increment_query(request.user, 'chat')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    chats = PlagarismChat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat.html', {'chats': chats})


@login_required
def review_file(request):
    if not check_query_limit(request.user):
        return JsonResponse({'error': 'Monthly query limit reached'}, status=403)

    if request.method == 'GET':
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
            code_content = data.get('code_content', '').strip()
            
            if not code_content:
                return JsonResponse({'error': 'Please provide style preferences'}, status=400)

            review, model_used = get_outfit_recommendation(code_content)

            PlagarismChat.objects.create(
                user=request.user,
                code=code_content,
                review=review,
                model_used=model_used,
                review_type='chat'
            )
            
            # Parse recommendation points cleanly
            if '*' in review:
                suggestion_points = [p.strip('-•* \t') for p in review.split('*') if p.strip('-•* \t')]
            elif '\n' in review:
                suggestion_points = [p.strip('-•* \t') for p in review.split('\n') if p.strip('-•* \t')]
            else:
                suggestion_points = [review.strip()]

            UserQueryCount.increment_query(request.user, 'chat')
            return JsonResponse({
                'career_suggestion': suggestion_points,
                'model_used': model_used
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def live(request):
    return render(request, 'active.html')


# Machine Learning: ResNet50 & Visual Search Recommendation
from PIL import Image
import numpy as np
import pickle
import tensorflow
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.layers import GlobalMaxPooling2D
import cv2
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors

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
    try:
        with open(image_path, 'rb') as img_file:
            return img_file.read()
    except Exception as e:
        print(f'Error reading image: {e}')
        return None

def extract_feature(img_path, model):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224))
    img = np.array(img)
    expand_img = np.expand_dims(img, axis=0)
    pre_image = preprocess_input(expand_img)
    result = model.predict(pre_image, verbose=0).flatten()
    normalized = result / norm(result)
    return normalized

def recommend(features, feature_list):
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)
    distance, indices = neighbors.kneighbors([features])
    return indices

@login_required
def fashion_recommend(request):
    if request.method == 'POST':
        if not check_query_limit(request.user):
            messages.error(request, 'Monthly query limit reached. Please contact admin to upgrade.')
            return render(request, 'fashion/upload.html')
            
        if 'image' in request.FILES:
            uploaded_file = request.FILES['image']
            fs = FileSystemStorage()
            
            filename = fs.save(f'uploads/{uploaded_file.name}', uploaded_file)
            uploaded_file_path = fs.path(filename)
            
            features = extract_feature(uploaded_file_path, model)
            indices = recommend(features, feature_list)
            
            recommended_images = []
            for idx in indices[0]:
                img_filename = os.path.basename(filenames[idx])
                recommended_images.append(img_filename)
            
            context = {
                'uploaded_image': f'/media/uploads/{uploaded_file.name}',
                'recommended_images': recommended_images
            }
            UserQueryCount.increment_query(request.user, 'file')

            return render(request, 'fashion/results.html', context)
        else:
            messages.error(request, 'Please choose an image file to upload.')
    
    return render(request, 'fashion/upload.html')

@login_required
def serve_fashion_image(request, image_name):
    image_path = os.path.join(IMAGES_DIR, image_name)
    image_data = serve_image(image_path)

    if image_data:
        return HttpResponse(image_data, content_type='image/jpeg')
    return HttpResponse(status=404)
