import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator


from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase


def upload_path(instance, filename):
    return os.path.join('blog', instance.blog.title, filename)


# Custom validators
hex_validator = RegexValidator(r'^[0-9A-F]*$')

class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author')
    image = models.ImageField(_('image'))
    short_bio = models.TextField(_('short bio'))
    credentials = models.CharField(_('credentials'), max_length=64)

    def get_full_name(self):
        if self.user.first_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return 'Annonimous Author'
    
    def __str__(self):
        return self.get_full_name()
        

class Tag(TagBase):
    pass
        

class TaggedPost(GenericTaggedItemBase):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )
    

class PublishedManager(TranslatableManager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')
    



class Category(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_('name'), max_length=20, db_index=True),
        slug = models.SlugField(_('slug'), max_length=20, unique=True),
    )
    tag_color = models.CharField(_('color'), max_length=6, unique=False, validators=[hex_validator], error_messages={'invalid': 'This value needs to be a hexadecimal color value'})

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def __str__(self):
        return self.name
    

class Post(TranslatableModel):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
    )
    
    translations = TranslatedFields(
        title = models.CharField(_('title'), max_length=250, unique=True),
        slug = models.SlugField(_('slug'), max_length=250),
        body = models.TextField(_('body')),
    )
    tags = TaggableManager(_('tags'), through=TaggedPost)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_('author'))
    publish = models.DateTimeField(_('publish'), default=timezone.now)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='draft')
    objects = TranslatableManager()
    published = PublishedManager()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='posts', null=True, verbose_name=_('category'))
    visits = models.IntegerField(_('visits'))

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])
    
    def has_been_updated(self):
        return True if self.created != self.updated else False
    
    def get_thumbnail_url(self):
        if self.images:
            return self.images.first().image.url
        return None
    
    
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
    
    
class NewsletterSubscriber(models.Model):
    email = models.EmailField(_('email'))
