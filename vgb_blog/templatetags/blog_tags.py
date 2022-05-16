import markdown

from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.db.models.functions import TruncMonth, TruncYear

from ..models import Post, Category

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def categories(instance):
    category_tags = instance.tags
    return ', '.join(category_tags.names()).lower()


@register.inclusion_tag('blog/tag_snippets/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.inclusion_tag('blog/tag_snippets/tags.html')
def post_tags(post, max_tags=2):
    tags = post.tags.all()[:max_tags]
    return {'tags': tags,}


@register.inclusion_tag('blog/tag_snippets/archives.html')
def get_archive_dates(month_limit=12):
    dates = Post.published.dates('publish', 'month')[:month_limit]
    return {'dates': dates,}


@register.inclusion_tag('blog/tag_snippets/categories.html')
def get_categories(lang, max_categories=99):
    '''Gets only the active categories list from the full CATEGORIES_CHOICES'''
    categories = Category.objects.language(lang).all()
    return {'categories': categories}


@register.inclusion_tag('blog/tag_snippets/popular.html')
def get_popular_posts(lang, count=5):
    '''Gets the most popular posts. TODO add popularity based on language'''
    popular_posts = Post.published.order_by('-visits')[:count]
    return {'popular_posts': popular_posts}