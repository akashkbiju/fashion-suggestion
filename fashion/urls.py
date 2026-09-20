from django.urls import path
from fashion import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Core
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('delete_user/<str:username>/', views.delete_user, name='delete_user'),

    # Chat / Reviews
    path('live/', views.live, name='live'),
    path('live-review/', views.review_code_live, name='live_review'),
    path('chat-review/', views.review_code_chat, name='chat_review'),
    path('file-review/', views.review_file, name='file_review'),

    # Fashion Image Recommendations
    path('fashion/', views.fashion_recommend, name='fashion_recommend'),
    path('fashion/image/<str:image_name>/', views.serve_fashion_image, name='serve_fashion_image'),
]
