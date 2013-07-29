from django.contrib import admin
from django.contrib.admin.util import unquote
from django.conf import settings
from django.core.exceptions import PermissionDenied
from newscenter import models, widgets, forms


USE_GUARDIAN = False
if 'guardian' in settings.INSTALLED_APPS:
    from guardian import admin as guardian_admin
    from guardian.shortcuts import (get_perms_for_model, get_perms,
                                    get_users_with_perms)
    GuardedModelAdmin = guardian_admin.GuardedModelAdmin
    USE_GUARDIAN = True
else:
    GuardedModelAdmin = admin.ModelAdmin


class ImageInline(admin.StackedInline):
    model = models.Image
    extra = 1


class ArticleInline(admin.StackedInline):
    model = models.Article
    extra = 0


class LocationAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


class NewsroomAdmin(GuardedModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


model_admin = admin.ModelAdmin
if 'reversion' in settings.INSTALLED_APPS:
    from reversion.admin import VersionAdmin
    model_admin = VersionAdmin


class ArticleAdmin(model_admin):
    inlines = [
        ImageInline,
    ]
    list_display = ('title', 'release_date', 'expire_date', 'active',
                    'featured', 'newsroom', )
    list_editable = ('active', 'featured', 'newsroom', )
    search_fields = ['title', 'body', 'teaser', ]
    list_filter = ('release_date', 'expire_date', 'newsroom', 'active',
                   'featured', 'categories', )
    prepopulated_fields = {'slug': ('title', )}
    date_heirarchy = 'release_date'
    filter_horizontal = ('categories', )
    fieldsets = (
        (None, {'fields': (('title', 'slug'), ('newsroom', 'active',
                'featured'), 'categories', 'location', 'teaser',
                'body', ('release_date', 'expire_date'), )}),
    )
    form = forms.ArticleAdminModelForm

    def __init__(self, model, admin_site):
        if USE_GUARDIAN:
            self.list_editable = ()
        super(ArticleAdmin, self).__init__(model, admin_site)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if USE_GUARDIAN:
            #Check to verify user has permissions to edit
            if (not request.user.is_superuser and
                    obj.newsroom and
                    get_users_with_perms(obj.newsroom) and not
                    u'edit_articles' in get_perms(request.user, obj.newsroom)):
                raise PermissionDenied
        return super(ArticleAdmin, self).change_view(request, object_id,
                                                     form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(ArticleAdmin, self).get_form(request, obj, **kwargs)

        class ModelFormMetaClass(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)
        return ModelFormMetaClass


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ['title', ]
    prepopulated_fields = {'slug': ('title', )}
    fieldsets = (
        ('Category', {'fields': ('title', 'slug')}),
    )


admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Newsroom, NewsroomAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Category, CategoryAdmin)
