from django.contrib import admin

from .models import (Answer, Article, Badge, BlogPost, Category, Course,
                     ForumComment, ForumThread, Post, Question, Quiz, Tag,
                     UserBadge, UserCourseEnrollment, UserCourseProgress,
                     UserProfile, UserQuizResult)


@admin.register(BlogPost)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'pub_date')

    @admin.action(description="Custom Action Description")
    def custom_action(self, request, queryset):
        # Your custom action logic here
        selected = queryset.update(some_field='some_value')
        self.message_user(
            request, f'{selected} items were updated successfully.')

    custom_action.short_description = "Custom Action Name"  # Button text


# admin.site.register(BlogPost)
admin.site.site_title = "Administrator"
admin.site.site_header = "Admin"

# myapp/admin.py


admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Course)
admin.site.register(UserCourseProgress)
admin.site.register(UserCourseEnrollment)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserQuizResult)
admin.site.register(ForumThread)
admin.site.register(ForumComment)
admin.site.register(Badge)
admin.site.register(UserBadge)
