from django.test import TestCase
from .models import BlogPost
from django.urls import reverse
from django.utils import timezone


class BlogPostTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content.",
            pub_date=timezone.now()
        )

    def test_blog_post_list_view(self):
        # Test the blog post list view
        response = self.client.get(reverse('blog_post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")

    def test_blog_post_detail_view(self):
        # Test the blog post detail view
        response = self.client.get(reverse('blog_post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")

    # Add more tests as needed

