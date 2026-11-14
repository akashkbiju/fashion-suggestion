# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required for account recovery and notifications.",
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True
    )


class FeedbackForm(forms.ModelForm):
    class Meta:
        from .models import Feedback
        model = Feedback
        fields = ['name', 'email', 'category', 'rating', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Name or Alias',
                'class': 'w-full px-4 py-3 bg-slate-900/60 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-rose-500 transition',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'name@example.com (optional)',
                'class': 'w-full px-4 py-3 bg-slate-900/60 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-rose-500 transition',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900 border border-white/10 rounded-xl text-white focus:outline-none focus:border-rose-500 transition',
            }),
            'rating': forms.HiddenInput(attrs={
                'id': 'ratingInput',
                'value': '5',
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Share your experience with our AI outfit suggestions, styling accuracy, or features you would love to see...',
                'rows': 4,
                'class': 'w-full px-4 py-3 bg-slate-900/60 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-rose-500 transition',
                'required': True,
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating or rating < 1 or rating > 5:
            return 5
        return rating

