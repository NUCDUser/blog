from .forms import NewsletterForm

def newsletter_subscribe(request):
    return {'newsletter_form': NewsletterForm}