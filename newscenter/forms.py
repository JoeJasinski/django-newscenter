from django import forms
from django.conf import settings
from django.db.models import get_model
from newscenter.widgets import SmallTextField
from newscenter.models import Newsroom

if 'guardian' in settings.INSTALLED_APPS:
    from guardian.shortcuts import get_users_with_perms, get_perms

class ArticleAdminModelForm(forms.ModelForm):
    if 'tinymce' in settings.INSTALLED_APPS:
        from tinymce.widgets import TinyMCE
        body = forms.CharField(widget=TinyMCE())
    teaser = forms.CharField(required=False, widget=SmallTextField())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ArticleAdminModelForm, self).__init__(*args, **kwargs)
    
    def clean_newsroom(self):
        newsroom = self.cleaned_data.get('newsroom')
        if newsroom is not None and 'guardian' in settings.INSTALLED_APPS:
            user = self.request.user
            if get_users_with_perms(newsroom):
                if (not self.instance.id and
                        not u'add_articles' in get_perms(user, newsroom)):
                    raise forms.ValidationError(
                        'You cannot post new articles to this newroom.'
                    )
                elif not u'edit_articles' in get_perms(user, newsroom):
                    raise forms.ValidationError(
                        'You cannot edit articles in this newroom.'
                    )
        return newsroom

    class Meta:
        model = get_model('newscenter', 'article')

