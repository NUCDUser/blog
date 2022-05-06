
from django.http import Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, TemplateView, View
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.utils.text import slugify
from django.utils.translation import get_language_from_request

from .models import Category, Post, Comment, Tag
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
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        return Post.published.order_by('publish')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        context['headline_posts'] = Post.published.order_by('created')[:3]
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
    searching_tags = False
    searching_text = False
    searching_category = False
    language = None
    
    def get_queryset(self):
        self.language = get_language_from_request(self.request)
        if 'query' in self.kwargs:
            self.searching_text = True
            self.query_keyword = self.kwargs['query']
            base_query = Post.published.language(self.language).annotate(similarity=TrigramSimilarity('translations__title', self.query_keyword)).filter(similarity__gt=0.1)
            print(base_query, "HERE", self.language)
            if 'order_by' not in self.request.GET or self.request.GET['order_by'] == 'relevance':
                return base_query.order_by('-similarity')
            queryset = self._order_by(base_query)
            return queryset
            
        elif 'year' and 'month' in self.kwargs:
            base_query = Post.published.filter(publish__year=self.kwargs['year'], publish__month=self.kwargs['month']).order_by('-publish')
            queryset = self._order_by(base_query)
            return queryset
        
        elif 'tag_name' in self.kwargs:
            self.searching_tags = True
            self.query_keyword = self.kwargs['tag_name']
            try:
                tag = Tag.objects.get(slug=self.query_keyword)
                print(tag)
                base_query = Post.published.language(self.language).all().filter(tags__in=[tag])
            except ObjectDoesNotExist:
                return Post.objects.none()
            queryset = self._order_by(base_query)
            return queryset
        
        elif 'category' in self.kwargs:
            self.searching_category = True
            self.query_keyword = self.kwargs['category']
            try:
                category_object = Category.objects.get(translations__name=self.query_keyword)
                base_query = Post.published.filter(category=category_object)
                queryset = self._order_by(base_query)
                return queryset
            except Exception as e:
                print(e)
                return Post.objects.none()
        else:
            return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # When at /search hide the search bar functionality of the nav
        context['at_search_page'] = True
        context['search_form'] = self._search_form_setup()
        context['total_results'] = self.object_list.count()
        context['page'] = self._paginator_setup()
        return context
    
    def _order_by(self, base_query):
        '''Orders the base queryset if specified on the request'''
        if 'order_by' in self.request.GET:
            if self.request.GET['order_by'] == 'newest':
                return base_query.order_by('-publish')
            elif self.request.GET['order_by'] == 'oldest':
                return base_query.order_by('publish')
            return base_query.order_by('-publish')
        return base_query
    
    def _search_form_setup(self):
        '''
        Returns a form object.
        Depending on the search, a placeholder for the form will be initialized
        reflecting the search term
        '''
        if self.searching_text:
            placeholder = self.kwargs['query']
        elif self.searching_category:
            placeholder = '@' + self.kwargs['category']
        elif self.searching_tags:
            placeholder = '#' + self.kwargs['tag_name']
        else:
            placeholder = ''
        return SearchForm(initial={'query': placeholder})
        
    def _paginator_setup(self):
        ''' Prepares the paginator object needed for the template pagination'''
        paginator = self.paginator_class(self.object_list, self.paginate_by)
        page = self.request.GET.get('page')
        return paginator.page(page)


class Detail(View):
    template_name = 'blog/detail.html'
    total_similar_posts = 4
    
    def get(self, request, year, month, day, post):
        post = get_object_or_404(Post, translations__slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)        
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