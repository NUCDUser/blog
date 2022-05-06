from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Category, Post, Comment, PostImages, Tag, TaggedPost

# Register your models here.
class PostImagesAdmin(admin.StackedInline):
    model = PostImages


@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('translations__body', 'translations__title')
    raw_id_field = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    inlines = (PostImagesAdmin,)
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}
    
    
@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
    
    
admin.site.register(Tag)