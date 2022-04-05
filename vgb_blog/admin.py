from django.contrib import admin
from .models import Post, Comment, PostImages

# Register your models here.
class PostImagesAdmin(admin.StackedInline):
    model = PostImages


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_field = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    inlines = PostImagesAdmin
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')