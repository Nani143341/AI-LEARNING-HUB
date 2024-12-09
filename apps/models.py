# myapp/models.py

import re

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100)
    popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)

    ROLE_CHOICES = [
        ('anonymous', 'Anonymous User'),
        ('free', 'Registered User (Free)'),
        ('premium', 'Premium User'),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='free')
    subscription_status = models.BooleanField(default=False)
    subscription_start_date = models.DateField(null=True, blank=True)
    interests = models.ManyToManyField(
        Interest, related_name='user_profiles', blank=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def has_premium_access(self):
        return self.subscription_status

    def is_subscription_active(self):
        return self.is_premium and self.subscription_end_date > timezone.now()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    is_premium = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, blank=True)
    interests = models.ManyToManyField(
        Interest, related_name='courses', blank=True)  # New field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_video_id(self):
        # Regex to extract YouTube video ID from various URL formats
        pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+|(?:v|e(?:mbed)?)|.*[?&]v=)|youtu\.be/)([^&]{11})'
        match = re.search(pattern, self.video_url)
        return match.group(1) if match else None

    def __str__(self):
        return self.title


class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)  # Percentage of course completed
    # New field to track completion
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s progress in {self.course.title}"


class UserCourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"Question for {self.quiz.title}: {self.text}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to '{self.question.text}': {self.text} (Correct: {self.is_correct})"


class UserQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)


class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ForumComment(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
