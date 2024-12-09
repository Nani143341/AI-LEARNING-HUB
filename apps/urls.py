"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from . import views
from .views import IndexView  # Import IndexView here
from .views import CourseSearchView

app_name = 'blog'  # Add this line to specify the app namespace


urlpatterns = [
    path('admin/', admin.site.urls),
    path('upgrade_success/', views.upgrade_success, name='upgrade_success'),
    path('hello/', views.hello, name='hello'),
    path('course/<slug:course_slug>/quiz/<int:quiz_id>/',
         views.quiz_detail_view, name='quiz_detail'),
    path('question/<int:question_id>/',
         views.question_detail, name='question_detail'),
    path('', views.home, name='home'),
    path('premium/', views.premium_dashboard, name='premium_dashboard'),
    path('accounts/profile/', views.user_profile, name='user_profile'),
    path('accounts/login/', views.custom_login_view, name='login_'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.register, name='register'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('trending-videos/', views.trending_videos, name='trending_videos'),
    path('', IndexView.as_view(), name='home'),
    path('blog/', views.BlogPostListView.as_view(), name='blog_post_list'),
    path('blog/<int:pk>/', views.BlogPostDetailView.as_view(),
         name='blog_post_detail'),
    path('blog/create/', views.create_blog_post, name='create_blog_post'),
    path('create-blog/', views.create_blog, name='create_blog_post'),
    path('about/', views.about, name='about.html'),
    path('edit-blog/<int:pk>/', views.edit_blog_post, name='edit_blog_post'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('articles/', views.article_list, name='article_list'),
    path('article/<int:id>/', views.article_detail, name='article_detail'),
    path('forum/', views.forum_list, name='forum_list'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('upgrade/', views.upgrade_to_premium, name='upgrade_to_premium'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('subscription-required/',
         views.subscription_required, name='subscription_required'),
    path('subscription-required/<slug:slug>/',
         views.subscription_required, name='subscription_required'),
    path('quiz/<int:quiz_id>/', views.quiz_view, name='quiz'),
    path('courses/search/', CourseSearchView.as_view(), name='course_search'),
    path('update-progress/<int:course_id>/',
         views.update_progress, name='update_progress'),
    # Ensure you have the course detail view
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('profile/', views.profile, name='profile'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),

]
