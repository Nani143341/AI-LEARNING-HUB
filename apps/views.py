
import pdb
import re
from datetime import timedelta

import requests
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import (get_object_or_404, redirect,  # Import redirect
                              render)
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .forms import (ArticleForm, BlogPostForm, CourseForm, ForumCommentForm,
                    ForumThreadForm, NewThreadForm, QuizForm,
                    UserRegistrationForm)
from .models import Course  # Import your Course model
from .models import (  # Adjust based on your actual model names; Import your models
    Article, BlogPost, ForumComment, ForumThread, Post, Question, Quiz, Tag,
    UserBadge, UserCourseEnrollment, UserCourseProgress, UserProfile,
    UserQuizResult)


@login_required
def edit_blog_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            # Redirect to the blog post list
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'edit_blog_post.html', {'form': form, 'post': post})


def custom_login_view(request):
    # Redirect authenticated users directly to the home page
    if request.user.is_authenticated:
        return redirect('blog:home')

    # Handle POST request for login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Check if user has a profile and redirect based on profile role
            if hasattr(user, 'profile'):
                if user.profile.is_premium:  # Redirect premium users
                    return redirect('blog:premium_dashboard')
                else:  # Redirect non-premium users
                    return redirect('blog:home')
            else:
                # Inform user to create a profile if it doesn't exist
                messages.info(
                    request, 'Your profile does not exist. Please create a profile to access the dashboard.')
                return redirect('blog:login_')

        else:
            # Show error message for invalid credentials
            messages.error(
                request, 'Incorrect Username or Password. Your profile does not exist. Please create a profile to access the dashboard.')

    # Context for rendering login page (can be used for additional data if needed)
    context = {}
    return render(request, 'login.html', context)


def loginPage(request):
    # Redirect authenticated users directly to the home page
    if request.user.is_authenticated:
        return redirect('blog:home')

    # Handle POST request for login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Check if user has a profile and redirect based on profile role
            if hasattr(user, 'profile'):
                if user.profile.is_premium:  # Redirect premium users
                    return redirect('blog:premium_dashboard')
                else:  # Redirect non-premium users
                    return redirect('blog:home')
            else:
                # Inform user to create a profile if it doesn't exist
                messages.info(
                    request, 'Your account does not exist. Please create an account to access the courses.')
                return redirect('blog:login_')

        else:
            # Show error message for invalid credentials
            messages.error(
                request, 'Incorrect Username or Password. Your account does not exist. Please create an account to access the courses.')

    # Context for rendering login page (can be used for additional data if needed)
    context = {}
    return render(request, 'login.html', context)


@login_required
def premium_dashboard(request):
    # Load premium courses and user progress
    courses = Course.objects.filter(is_premium=True)
    # user_progress = request.user.get_course_progress()
    return render(request, 'premium_dashboard.html', {'courses': courses})


# youtube_service.py

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def search_educational_videos(query):
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY
        )
        request = youtube.search().list(
            q=query + ' tutorial',  # Add additional keywords to narrow down the search
            part='snippet',
            type='video',
            maxResults=5,
            videoCategoryId='27',
            safeSearch='strict'
        )
        response = request.execute()
        return [item['id']['videoId'] for item in response.get('items', [])]

    except HttpError as e:
        error_reason = e.content.decode("utf-8")
        print(f"YouTube API Error: {error_reason}")
        # Handle the error as needed, e.g., log it or return an empty list
        return []

# In your view


def recommended_courses(request):
    user_profile = request.user.userprofile
    recommended_courses = Course.objects.filter(
        interests__in=user_profile.interests.all()).distinct()
    return render(request, 'courses/recommended_courses.html', {'courses': recommended_courses})


# Redirect to the login page if not authenticated
@login_required
def logoutUser(request):
    logout(request)
    return redirect(reverse('blog:login'))


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create user profile
            profile = UserProfile.objects.create(user=user)

            # Assign interests
            interests = form.cleaned_data.get('interests')
            if interests:
                profile.interests.set(interests)

            profile.save()
            login(request, user)
            return redirect('blog:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog_post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q')

        if query:
            return BlogPost.objects.filter(Q(title__icontains=query))
        else:
            return BlogPost.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_posts = Post.objects.all().order_by('-pub_date')[:5]
        popular_tags = Tag.objects.filter(popular=True)
        context['latest_posts'] = latest_posts
        context['popular_tags'] = popular_tags
        context['query'] = self.request.GET.get('q', '')
        context['message'] = f'Search results for "{context["query"]}"' if context['query'] else 'All Blog Posts'
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_post_detail.html'
    context_object_name = 'post'

    # Override the get_context_data method to add extra context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_posts = Post.objects.all().order_by('-pub_date')[:5]
        popular_tags = Tag.objects.filter(popular=True)
        context['latest_posts'] = latest_posts
        context['popular_tags'] = popular_tags
        return context


@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.pub_date = timezone.now()
            form.save()
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog_post_form.html', {'form': form})


@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.pub_date = timezone.now()
            form.save()
            return redirect('blog:blog_post_list')
    else:
        form = BlogPostForm()

    return render(request, 'create_blog_post.html', {'form': form})


@login_required
def blog_post_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog_post_list.html', {'posts': posts})


@login_required
def about(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_post_list')
    else:
        form = BlogPostForm()

    context = {
        'form': form,
        'arbitrary_date': 'September 37, 2023',
        'creator_name': 'The Hot News LLC',
        'current_year': 2023,
    }
    return render(request, 'about.html', context)


def hello(request):
    return HttpResponse("Hello, Django!")


class IndexView(TemplateView):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        # Retrieve username and password from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Log the user in
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Only log in if the user is found and authentication is successful
            login(request, user)
            return redirect('blog:index')
        else:
            # User not authenticated, render the login page with an error message
            error_message = "Authentication failed. Please check your username/password. New user register account"
            return render(request, self.template_name, {'error_message': error_message})


@login_required
def update_progress(request, course_id):
    # Fetch the course based on ID
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        # Get or create course progress for the current user
        course_progress, created = UserCourseProgress.objects.get_or_create(
            course=course, user=request.user
        )

        # Update the progress, ensuring it does not exceed 100%
        course_progress.progress += 25
        if course_progress.progress > 100:
            course_progress.progress = 100  # Cap progress at 100

        # Check if progress is now 100%
        if course_progress.progress == 100:
            # Mark the course as completed
            course_progress.completed = True
            course_progress.save()

            # Update the leaderboard
            update_leaderboard(request.user, course)

        # Save the progress
        course_progress.save()

        # Redirect to the course detail page with the updated progress
        return redirect('blog:course_detail', slug=course.slug)

    return redirect('blog:course_detail', slug=course.slug)


def update_leaderboard(user, course):
    # Define how many points to award for completing a course
    points_awarded = 10  # Example points for completing a course

    # Fetch the user's profile
    user_profile = user.userprofile

    # Update points
    user_profile.points += points_awarded
    user_profile.save()


@login_required
def leaderboard_view(request):
    # Annotate user profiles with average quiz scores and completed courses
    top_users = UserProfile.objects.annotate(
        # Average score from quiz results
        avg_score=Avg('userquizresult__score'),
        course_count=Count('usercourseprogress', filter=models.Q(
            usercourseprogress__progress=100))  # Count of completed courses
    ).order_by('-avg_score', '-course_count')[:10]  # Get top 10 users

    return render(request, 'leaderboard.html', {
        'top_users': top_users
    })


@login_required
def home(request):
    # Replace with the logic to get featured courses
    courses = Course.objects.all()
    # Replace with your logic for articles
    articles = Article.objects.all()[:5]
    # Filter out premium courses
    premium_courses = courses.filter(is_premium=True)
    # Filter out non-premium courses
    regular_courses = courses.filter(is_premium=False)

    # Sample AI news data
    news_feed = [
        {
            "title": "OpenAI Introduces New ChatGPT Model",
            # Replace with actual announcement
            "url": "https://openai.com/blog/introducing-chatgpt-4/",
            "source": "OpenAI Blog"
        },
        {
            "title": "AI Breakthrough in Healthcare: Diagnosing Diseases Faster",
            "url": "https://www.weforum.org/agenda/2024/09/how-ai-is-improving-diagnostics-and-health-outcomes-transforming-healthcare",
            "source": "World Economic Forum"  # Updated source based on real article
        },
        {
            "title": "Google's AI Strategy in 2024",
            # Example article
            "url": "https://www.theverge.com/2024/8/12/22073124/google-ai-strategy-deepmind-lamda",
            "source": "The Verge"
        },
        {
            "title": "How AI is Transforming the Finance Industry",
            "url": "https://www.bloomberg.com/news/articles/2024-09-26/how-ai-is-reshaping-finance",
            "source": "Bloomberg"
        },
        {
            "title": "Top AI Trends to Watch in 2024",
            "url": "https://www.forbes.com/sites/bernardmarr/2024/01/10/top-10-artificial-intelligence-trends-to-watch-in-2024/",
            "source": "Forbes"
        },
        {
            "title": "AI Regulation on the Horizon",
            "url": "https://www.reuters.com/technology/governments-race-regulate-ai-tools-2023-10-13/",
            "source": "Reuters"
        },
        {
            "title": "Bias in AI: Mitigating Algorithmic Inequality",
            "url": "https://www.wired.com/story/recruiters-ai-application-overload/",
            "source": "Wired"
        },
        {
            "title": "AI-Powered Customer Service Revolutionizes Interactions",
            "url": "https://www.forbes.com/sites/sunilrajaraman/2024/06/18/ai-driven-customer-service-is-gaining-steam/",
            "source": "Forbes"
        },
        {
            "title": "AI Optimizes Supply Chains for Efficiency and Cost Savings",
            "url": "https://www.mckinsey.com/industries/metals-and-mining/our-insights/succeeding-in-the-ai-supply-chain-revolution",
            "source": "McKinsey & Company"
        },
        {
            "title": "AI Fights Climate Change: Predicting Disasters and Saving Energy",
            "url": "https://www.technologyreview.com/topic/climate-change/",
            "source": "MIT Technology Review"
        },
        {
            "title": "AI Protects Endangered Species and Combats Poaching",
            "url": "https://www.nationalgeographic.com/animals/article/artificial-intelligence-counts-wild-animals",
            "source": "National Geographic"
        }
    ]

    context = {
        'courses': courses,
        'premium_courses': premium_courses,
        'regular_courses': regular_courses,
        'articles': articles,
        'news_feed': news_feed
    }

    return render(request, 'index.html', context)


# views.py
@login_required
def upgrade_success(request):
    """View for displaying the user's profile after a successful upgrade."""
    user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'upgrade_success.html', {'user_profile': user_profile})


@login_required
def upgrade_to_premium(request):
    """View for upgrading a user to a premium subscription."""
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        # Assume there's a valid payment or other verification process
        # Here, we directly update the subscription status
        user_profile.subscription_status = True
        user_profile.subscription_start_date = timezone.now().date()
        user_profile.subscription_end_date = timezone.now(
        ).date() + timedelta(days=365)  # 1-year subscription
        user_profile.save()
        # Retrieve the course title from session and redirect back to the course
        course_title = request.session.get('course_title', None)
        if course_title:
            # Convert the course title back to slug format and redirect
            course_slug = course_title.replace(' ', '-')
            return redirect('blog:course_detail', slug=course_slug)

        # If no course was found in the session, redirect to the home page or course list
        return redirect('blog:upgrade_success')

    return render(request, 'upgrade_to_premium.html')


@login_required
def process_payment(request):
    """Handles payment processing for upgrading to premium."""
    if request.method == 'POST':
        payment_plan = request.POST.get('payment_plan')
        # In a real app, payment gateway integration would be here

        # Assuming payment is successful
        request.user.is_premium = True  # Set the user as premium
        request.user.save()

        messages.success(
            request, "Payment successful! You've been upgraded to Premium.")
        return redirect('blog:home')
    else:
        messages.error(request, "Invalid payment request.")
        return redirect('upgrade_to_premium')


@login_required
def user_profile(request):
    # Replace with the logic to get featured courses
    courses = Course.objects.all()
    # Replace with your logic for articles
    articles = Article.objects.all()[:5]
    # Filter out premium courses
    premium_courses = courses.filter(is_premium=True)
    # Filter out non-premium courses
    regular_courses = courses.filter(is_premium=False)

    # Sample AI news data
    news_feed = [
        {
            "title": "OpenAI Introduces New ChatGPT Model",
            # Replace with actual announcement
            "url": "https://openai.com/blog/introducing-chatgpt-4/",
            "source": "OpenAI Blog"
        },
        {
            "title": "AI Breakthrough in Healthcare: Diagnosing Diseases Faster",
            "url": "https://www.weforum.org/agenda/2024/09/how-ai-is-improving-diagnostics-and-health-outcomes-transforming-healthcare",
            "source": "World Economic Forum"  # Updated source based on real article
        },
        {
            "title": "Google's AI Strategy in 2024",
            # Example article
            "url": "https://www.theverge.com/2024/8/12/22073124/google-ai-strategy-deepmind-lamda",
            "source": "The Verge"
        },
        {
            "title": "How AI is Transforming the Finance Industry",
            "url": "https://www.bloomberg.com/news/articles/2024-09-26/how-ai-is-reshaping-finance",
            "source": "Bloomberg"
        },
        {
            "title": "Top AI Trends to Watch in 2024",
            "url": "https://www.forbes.com/sites/bernardmarr/2024/01/10/top-10-artificial-intelligence-trends-to-watch-in-2024/",
            "source": "Forbes"
        },
        {
            "title": "AI Regulation on the Horizon",
            "url": "https://www.reuters.com/technology/governments-race-regulate-ai-tools-2023-10-13/",
            "source": "Reuters"
        },
        {
            "title": "Bias in AI: Mitigating Algorithmic Inequality",
            "url": "https://www.wired.com/story/recruiters-ai-application-overload/",
            "source": "Wired"
        },
        {
            "title": "AI-Powered Customer Service Revolutionizes Interactions",
            "url": "https://www.forbes.com/sites/sunilrajaraman/2024/06/18/ai-driven-customer-service-is-gaining-steam/",
            "source": "Forbes"
        },
        {
            "title": "AI Optimizes Supply Chains for Efficiency and Cost Savings",
            "url": "https://www.mckinsey.com/industries/metals-and-mining/our-insights/succeeding-in-the-ai-supply-chain-revolution",
            "source": "McKinsey & Company"
        },
        {
            "title": "AI Fights Climate Change: Predicting Disasters and Saving Energy",
            "url": "https://www.technologyreview.com/topic/climate-change/",
            "source": "MIT Technology Review"
        },
        {
            "title": "AI Protects Endangered Species and Combats Poaching",
            "url": "https://www.nationalgeographic.com/animals/article/artificial-intelligence-counts-wild-animals",
            "source": "National Geographic"
        }
    ]

    context = {
        'courses': courses,
        'premium_courses': premium_courses,
        'regular_courses': regular_courses,
        'articles': articles,
        'news_feed': news_feed
    }

    return render(request, 'index.html', context)


def quiz_detail(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()
    context = {'quiz': quiz, 'questions': questions}
    return render(request, 'quiz_detail.html', context)


def quiz_detail_view(request, course_slug, quiz_id):
    course = get_object_or_404(Course, slug=course_slug)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    questions = quiz.questions.all()

    context = {
        'course': course,
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quiz_detail.html', context)


def question_detail(request, question_id):
    question = Question.objects.get(id=question_id)
    answers = question.answers.all()
    context = {'question': question, 'answers': answers}
    return render(request, 'question_detail.html', context)


@login_required
def quiz_view(request, quiz_id):
    # Fetch the quiz or return a 404 if not found
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Fetch all related questions with their answers
    questions = quiz.questions.prefetch_related('answers')

    if request.method == 'POST':
        score = 0
        user_answers = {}  # Store user's answers for display
        failed_questions = []  # Store questions the user got wrong

        for question in questions:
            # Get the user's selected answer
            user_answer = request.POST.get(str(question.id))
            user_answers[question.id] = user_answer

            # Collect correct answer texts
            correct_answer_texts = [
                answer.text for answer in question.answers.all() if answer.is_correct]

            # Check if the user's answer is correct
            if user_answer and str(user_answer) in [str(answer.id) for answer in question.answers.all() if answer.is_correct]:
                score += 1  # Increment score for correct answers
            else:
                failed_questions.append({
                    'question': question.text,
                    'user_answer': user_answer,
                    'correct_answers': correct_answer_texts
                })

        # Calculate total number of questions
        total_questions = questions.count()  # Total number of questions

        # Save the quiz result for the user
        UserQuizResult.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'score': score}
        )

        # Prepare results
        results = {
            'score': score,
            'total_questions': total_questions,
            'user_answers': user_answers,
            'failed_questions': failed_questions,
        }

        # Render the result page with the score and results
        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'results': results,  # Pass the results to the template
        })

    # Render the quiz page with questions and their answer options
    return render(request, 'quiz.html', {'quiz': quiz, 'questions': questions})


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch user profile and enrolled courses
    user_profile = request.user.userprofile
    enrolled_courses = UserCourseEnrollment.objects.filter(user=request.user)
    print(enrolled_courses)
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'enrolled_courses': enrolled_courses
    })


def trending_videos(request):
    # Example list of video IDs for trending news and courses
    trending_news_videos = [
        "gqUQbjsYZLQ", "Ih-SoOrvl4Q", "mKYbEk-kAsA", "SMnBnGQqlR4", "spsG4G2sbrw"
    ]
    popular_courses_videos = [
        "ad79nYk2keg", "gZmobeGL0Yg", "Gv9_4yMHFhI", "E0Hmnixke2g"
    ]
    context = {
        'trending_news_videos': trending_news_videos,
        'popular_courses_videos': popular_courses_videos,
    }
    return render(request, 'trending_videos.html', context)


def article_list(request):
    articles = Article.objects.all()
    if not request.user.is_authenticated or not request.user.userprofile.is_premium:
        articles = articles.filter(is_premium=False)
    return render(request, 'article_list.html', {'articles': articles})


@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.is_premium and not request.user.userprofile.is_premium:
        return redirect('subscription_required')
    return render(request, 'article_detail.html', {'article': article})


@login_required
def course_list(request):
    # Retrieve all premium and regular courses
    premium_courses = Course.objects.filter(is_premium=True)
    regular_courses = Course.objects.filter(is_premium=False)

    # Retrieve the courses the user is enrolled in
    enrolled_courses = UserCourseEnrollment.objects.filter(
        user=request.user).select_related('course')

    return render(request, 'course_list.html', {
        'premium_courses': premium_courses,
        'regular_courses': regular_courses,
        'enrolled_courses': enrolled_courses,
    })


def subscription_required(request):
    # Get the course title from the session
    course_title = request.session.get('course_title', None)

    if not course_title:
        # Handle case where course_title is missing
        return redirect('blog:course_list')  # or some error page

    # Retrieve the course using the title
    course = get_object_or_404(Course, title__iexact=course_title)

    # Render the explanation page with the course details
    return render(request, 'subscription_required.html', {'course': course, 'course_title': course_title})


# youtube_service.py

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def search_educational_videos(query):
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY
        )
        request = youtube.search().list(
            q=query + ' tutorial',  # Add additional keywords to narrow down the search
            part='snippet',
            type='video',
            maxResults=5,
            videoCategoryId='27',
            safeSearch='strict'
        )
        response = request.execute()
        return [item['id']['videoId'] for item in response.get('items', [])]

    except HttpError as e:
        error_reason = e.content.decode("utf-8")
        print(f"YouTube API Error: {error_reason}")
        # Handle the error as needed, e.g., log it or return an empty list
        return []


@login_required
def course_detail(request, slug):
    course_title = slug.replace('-', ' ')
    course = get_object_or_404(Course, title__iexact=course_title)

    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponse("Error: no user profile")

    if course.is_premium and not user_profile.has_premium_access():
        request.session['course_title'] = course_title
        return redirect('blog:subscription_required')

    progress, progress_created = UserCourseProgress.objects.get_or_create(
        user=request.user, course=course
    )

    video_ids = search_educational_videos(course.title)
    first_video_id = video_ids[0] if video_ids else None

    if request.method == 'POST':
        if 'enroll' in request.POST:
            UserCourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course
            )
            progress.progress = 0
            progress.save()

        elif 'start_quiz' in request.POST:
            quiz_id = request.POST.get('quiz_id')
            if quiz_id:
                return redirect('blog:quiz', quiz_id=quiz_id)

    is_enrolled = UserCourseEnrollment.objects.filter(
        user=request.user, course=course).exists()

    quizzes = Quiz.objects.filter(course=course)

    # Retrieve quiz results for the current user
    quiz_results = UserQuizResult.objects.filter(
        user=request.user, quiz__in=quizzes)

    return render(request, 'course_detail.html', {
        'course': course,
        'progress': progress,
        'is_enrolled': is_enrolled,
        'quizzes': quizzes,
        'first_video_id': first_video_id,
        'quiz_results': quiz_results,  # Pass the quiz results to the template
    })


# views.py


class CourseSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            # Filter courses based on the search query
            courses = Course.objects.filter(
                title__icontains=query)  # Adjust as needed
        else:
            courses = Course.objects.none()  # No courses found if no query

        context = {
            'courses': courses,
            'query': query,
        }
        return render(request, 'course_search_results.html', context)


def fetch_video_details(video_id):
    """Fetch video details from YouTube API."""
    api_key = settings.YOUTUBE_API_KEY
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None  # Handle error or return a default value


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.is_premium and not request.user.userprofile.is_premium:
        return redirect('subscription_required')
    # Implement quiz-taking logic here
    return render(request, 'take_quiz.html', {'quiz': quiz})


# views.py


def thread_detail(request, thread_id):
    # Retrieve the forum thread or return a 404 error if not found
    thread = get_object_or_404(ForumThread, id=thread_id)

    if request.method == 'POST':
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            # Create a new comment instance but don't save yet
            comment = form.save(commit=False)
            comment.thread = thread  # Associate the comment with the thread
            comment.author = request.user  # Set the author to the current user
            comment.save()  # Save the comment to the database

            # Redirect to the same thread detail page after saving the comment
            # Adjust namespace if necessary
            return redirect('blog:thread_detail', thread_id=thread.id)
    else:
        form = ForumCommentForm()  # Initialize an empty form for GET requests

    # Retrieve all comments related to this thread
    comments = thread.forumcomment_set.all()

    # Render the template with the thread, comments, and form context
    return render(request, 'thread_detail.html', {
        'thread': thread,
        'comments': comments,
        'form': form,
    })


@login_required
def forum_list(request):
    # Annotate threads with the count of related comments
    threads = ForumThread.objects.annotate(comment_count=Count('forumcomment'))

    if request.method == 'POST':
        form = NewThreadForm(request.POST)
        if form.is_valid():
            new_thread = form.save(commit=False)
            new_thread.author = request.user
            new_thread.save()
            # Update this to match your URL pattern
            return redirect('blog:forum_list')
    else:
        form = NewThreadForm()

    return render(request, 'forum_list.html', {'threads': threads, 'form': form})


@login_required
def forum_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    # Retrieve all comments related to the thread
    comments = thread.forumcomment_set.all()
    if request.method == 'POST':
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thread = thread
            comment.author = request.user
            comment.save()
            # Redirect to the same thread
            return redirect('blog:forum_thread', thread_id=thread.id)
    else:
        form = ForumCommentForm()
    return render(request, 'forum_thread.html', {'thread': thread, 'comments': comments, 'form': form})


@login_required
def create_thread(request):
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()
            return redirect('forum_thread', thread_id=thread.id)
    else:
        form = ForumThreadForm()
    return render(request, 'create_thread.html', {'form': form})


def leaderboard(request):
    top_users = UserProfile.objects.annotate(
        avg_score=Avg('user__userquizresult__score'),
        course_count=Count('user__usercourseprogress', filter=models.Q(
            user__usercourseprogress__progress=100))
    ).order_by('-avg_score', '-course_count')[:10]
    return render(request, 'leaderboard.html', {'top_users': top_users})


@login_required
def subscription_management(request):
    # Implement subscription management logic here (e.g., using Stripe)
    return render(request, 'subscription_management.html')
