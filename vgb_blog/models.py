import os
from sre_parse import CATEGORIES
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from taggit.managers import TaggableManager

# Create your models here.
def upload_path(instance, filename):
    return os.path.join('blog', instance.blog.title, filename)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    CATEGORIES_CHOICES = (
        ('test', 'Test'),
        ('tutorials', 'Tutorials'),
        ('guides', 'Guides'),
        ('reeds', 'Reeds'),
        ('lifestyle', 'Lifestyle'),
        ('mental_health', 'Mental Health'),
        ('psyche', 'Psyche'),
        ('bassoon', 'Bassoon'),
        ('computers', 'Computers'),
        ('technology', 'Technology'),
        ('production', 'Production'),
        ('web-dev', 'Web Development'),
        ('personal', 'Personal'),
        ('shower_thoughts', 'Shower Thoughts'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()
    category = models.CharField(max_length=20, choices=CATEGORIES_CHOICES, default='test')

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])
    
    def has_been_updated(self):
        return True if self.created != self.updated else False
    
class PostImages(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to=upload_path)
    blog = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    source_or_author = models.CharField(max_length=128, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('created',)
        
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
