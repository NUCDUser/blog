from cProfile import label
from django import forms
from .models import Comment

class SearchForm(forms.Form):
    query = forms.CharField(label='')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['query'].widget.attrs['class'] = 'form-control'
        self.fields['query'].widget.attrs['placeholder'] = 'Search'
    

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)
    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        