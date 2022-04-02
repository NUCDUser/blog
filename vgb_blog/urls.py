from django.urls import path
from .feeds import LatestPostsFeed
from . import views

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('search/', views.post_search, name='post_search'),
    
    #RSS
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('index', views.Index.as_view(), name='index'),
    path('detail', views.TempDetail.as_view(), name='detail'),
    path('search2/', views.TempSearch.as_view(), name='search2'),
]