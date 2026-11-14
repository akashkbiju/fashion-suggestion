# models.py
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    is_owner = models.BooleanField(default=False)
    query_limit = models.IntegerField(default=100)  # Monthly query limit

class PlagarismChat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.TextField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    model_used = models.CharField(max_length=20)
    review_type = models.CharField(max_length=20)  # 'live', 'chat', or 'file'

class UserQueryCount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.DateField()  # Stores first day of the month
    live_queries = models.IntegerField(default=0)
    chat_queries = models.IntegerField(default=0)
    file_queries = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'month']

    @classmethod
    def increment_query(cls, user, query_type):
        current_month = timezone.now().date().replace(day=1)
        query_count, _ = cls.objects.get_or_create(
            user=user,
            month=current_month
        )
        
        if query_type == 'live':
            query_count.live_queries += 1
        elif query_type == 'chat':
            query_count.chat_queries += 1
        elif query_type == 'file':
            query_count.file_queries += 1
            
        query_count.save()


class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('outfit_recs', 'Outfit Recommendations'),
        ('piece_inspo', 'Piece Inspo & Matching'),
        ('ui_ux', 'Design & User Experience'),
        ('feature_request', 'Feature Request / Idea'),
        ('general', 'General Feedback'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    rating = models.PositiveSmallIntegerField(default=5)  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}★ ({self.get_category_display()})"
