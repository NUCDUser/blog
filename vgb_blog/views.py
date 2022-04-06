from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, TemplateView, View
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm

# Create your views here.
class Index(ListView):
    template_name = 'blog/index.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context
    

def test(request):
    dates = Post.published.dates('publish', 'month')
    print(dates)
    return HttpResponse('TEST')
    
class SearchView(ListView):
    template_name = 'blog/search.html'
    context_object_name = 'results'
    paginate_by = 9
    
    def get_queryset(self):
        if 'query' in self.request.GET:
            form = SearchForm(self.request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                return Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1).order_by('-similarity')
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # when at /search hide the search bar functionality of the nav
        context['searching'] = True 
        context['search_form'] = SearchForm()
        paginator = Paginator(self.object_list, self.paginate_by)

        page = self.request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['results'] = posts
        if 'query' in self.request.GET:
            context['search_form'] = SearchForm(initial={'query':self.request.GET['query']})
        return context

class PostListView(ListView):
    paginate_by = 3
    template_name = 'blog/search.html'
    
    def get_queryset(self):
        if self.kwargs['tag_slug']:
            tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
            return Post.published.all().filter(tags__in=[tag])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        paginator = Paginator(self.object_list, self.paginate_by)

        page = self.request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['results'] = posts
        return context


class Detail(View):
    template_name = 'blog/detail.html'
    total_similar_posts = 4
    
    def get(self, request):
        post = get_object_or_404(Post, slug=self.kwargs['post'], status='published', publish__year=self.kwargs['year'], publish__month=self.kwargs['month'], publish__day=self.kwargs['day'])
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:self.total_similar_posts]
        context = {
            'similar_posts': similar_posts,
        }
        return render(request, self.template_name, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    
    new_comment = None
    
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
        
    post_tags_ids = post.tags.values_list('id', flat=True) # Returns a list of tag IDs
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
            
    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
    }
    return render(request, 'blog/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Send Email TODO
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]} recommends you read {post.title}'
            message = f'Read {post.title} at {post_url}\n\n' f'{cd["name"]}\' comments: {cd["comments"]}'
            send_mail(subject, message, 'admin@vgbassoonist.com', [cd["to"]])
            sent = True

    else:
        form = EmailPostForm()
        
    context = {
        'post':post,
        'form': form,
        'sent': sent
        }
    return render(request, 'blog/post/share.html', context)


# def post_list(request, tag_slug=None):
#     object_list = Post.published.all()
#     tag = None
    
#     if tag_slug:
#         tag = get_object_or_404(Tag, slug=tag_slug)
#         object_list = object_list.filter(tags__in=[tag])
        
#     paginator = Paginator(object_list, 3)
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
        
#     context = {
#         'page': page,
#         'posts': posts,
#         'tag': tag,
#         }
#     return render(request, 'blog/post/list.html', context)


# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
#             search_query = SearchQuery(query)
#             # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
#             results = Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1).order_by('-similarity')
            
#     context = {
#         'form': form,
#         'query': query,
#         'results': results,
#     }    
#     return render(request, 'blog/post/search.html', context)