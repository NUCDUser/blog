from django.urls import path
from .feeds import LatestPostsFeed
from . import views

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.Index.as_view(), name='index'),
    path('search/<str:query>/', views.SearchView.as_view(), name='post_list_by_query'),
    path('search/category/<str:category>/', views.SearchView.as_view(), name='post_list_by_category'),
    path('search/tag/<slug:tag_name>/', views.SearchView.as_view(), name='post_list_by_tag'),
    path('search/dates/<int:year>/<int:month>/', views.SearchView.as_view(), name='post_list_by_date'),
    # path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.Detail.as_view(), name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('test/', views.test),
    
    #RSS
    path('feed/', LatestPostsFeed(), name='post_feed'),
]