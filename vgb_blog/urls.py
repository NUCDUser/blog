from django.urls import path
from django.utils.translation import gettext_lazy as _

from .feeds import LatestPostsFeed
from . import views

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.Index.as_view(), name='index'),
    path(_('search/')+'<str:query>/', views.SearchView.as_view(search_criteria=_('search')), name='post_list_by_query'),
    path(_('search/category/')+'<str:category>/', views.SearchView.as_view(search_criteria=_('category')), name='post_list_by_category'),
    path(_('search/tag/')+'<slug:tag_name>/', views.SearchView.as_view(search_criteria=_('tag')), name='post_list_by_tag'),
    path(_('search/date/')+'<int:year>/<int:month>/', views.SearchView.as_view(search_criteria=_('date')), name='post_list_by_date'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.Detail.as_view(), name='post_detail'),
    path('<int:post_id>/'+_('share/'), views.post_share, name='post_share'),
    path('test/', views.test),
    
    #RSS
    path('feed/', LatestPostsFeed(), name='post_feed'),
]