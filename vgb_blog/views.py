from django.http import Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, TemplateView, View
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.utils.text import slugify

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm

class CustomPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except PageNotAnInteger:
            return 1
        except EmptyPage:
            return self.num_pages
        
        
def slug_to_string(slug):
    return slug.replace('-', ' ')

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
    paginate_by = 5
    context_object_name = 'results'
    paginator_class = CustomPaginator
    query_keyword = None
    
    def get_queryset(self):
        if 'query' in self.request.GET:
            form = SearchForm(self.request.GET)
            if form.is_valid():
                self.query_keyword = form.cleaned_data['query']
                base_query = Post.published.annotate(similarity=TrigramSimilarity('title', self.query_keyword)).filter(similarity__gt=0.1)
                if 'order_by' in self.request.GET:
                    if self.request.GET['order_by'] == 'newest':
                        return base_query.order_by('-publish')
                    elif self.request.GET['order_by'] == 'oldest':
                        return base_query.order_by('publish')
                return base_query.order_by('-similarity')
            
        elif 'year' and 'month' in self.kwargs:
            return Post.published.filter(publish__year=self.kwargs['year'], publish__month=self.kwargs['month'])
        
        elif 'slug' in self.request.GET:
            self.query_keyword = self.request.GET['slug']
            try:
                tag = Tag.objects.get(slug=slugify(self.query_keyword))
                return Post.published.all().filter(tags__in=[tag])
            except ObjectDoesNotExist:
                pass # Will go to the default return of the get_queryset function
            
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # when at /search hide the search bar functionality of the nav
        context['searching'] = True 
        context['search_form'] = SearchForm()
        context['total_results'] = self.object_list.count()
        paginator = self.paginator_class(self.object_list, self.paginate_by)

        page = self.request.GET.get('page')
        paginator_pages = paginator.page(page)
        context['page'] = paginator_pages
        if self.query_keyword:
            context['search_form'] = SearchForm(initial={'query':self.query_keyword})
            context['query'] = self.query_keyword
        return context

class PostListView(ListView):
    template_name = 'blog/search.html'
    paginate_by = 5
    context_object_name = 'results'
    paginator_class = CustomPaginator
    query_keyword = None
    
    def get_queryset(self):
        if 'slug' in self.request.GET:
            self.query_keyword = self.request.GET['slug']
            try:
                tag = Tag.objects.get(slug=slugify(self.query_keyword))
                return Post.published.all().filter(tags__in=[tag])
            except ObjectDoesNotExist:
                pass
        return Post.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['searching'] = True
        context['searching_tags'] = True
        context['search_form'] = SearchForm()
        if self.query_keyword:
            context['search_form'] = SearchForm(initial={'query': '#' +  self.query_keyword})
        context['total_results'] = self.object_list.count()
        paginator = self.paginator_class(self.object_list, self.paginate_by)

        page = self.request.GET.get('page')
        paginator_pages = paginator.page(page)
        context['page'] = paginator_pages
        return context


class Detail(View):
    template_name = 'blog/detail.html'
    total_similar_posts = 4
    
    def get(self, request, year, month, day, post):
        post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)        
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:self.total_similar_posts]
        context = {
            'post': post,
            'similar_posts': similar_posts,
            'search_form': SearchForm(),
        }
        return render(request, self.template_name, context)


# def post_detail(request, year, month, day, post):
#     post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
#     comments = post.comments.filter(active=True)
    
#     new_comment = None
    
#     if request.method == 'POST':
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.post = post
#             new_comment.save()
#     else:
#         comment_form = CommentForm()
        
#     post_tags_ids = post.tags.values_list('id', flat=True) # Returns a list of tag IDs
#     similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
#     similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
            
#     context = {
#         'post': post,
#         'comments': comments,
#         'new_comment': new_comment,
#         'comment_form': comment_form,
#         'similar_posts': similar_posts,
#     }
#     return render(request, 'blog/detail.html', context)


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