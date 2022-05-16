from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, NewsletterSubscriber

class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Search'),
        'id': 'search-input',
        'aria-label': 'search bar',
    }))
    

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)
    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = _('Email address')
        self.fields['email'].widget.attrs['id'] = 'inputEmail'
        self.fields['email'].widget.attrs['aria-label'] = 'input email address'
        self.fields['email'].widget.attrs['class'] = 'form-control rounded-0'
        