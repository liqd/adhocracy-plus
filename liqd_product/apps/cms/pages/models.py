from django.contrib import messages
from django.db import models
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from liqd_product.apps.cms.updates.forms import KeepMeUpdatedEmailForm


class HomePage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image",
        help_text="The Image that is shown on top of the page"
    )
    subtitle = models.CharField(
        max_length=500, blank=True, verbose_name="Subtitle")
    body = RichTextField(blank=True)

    subpage_types = ['liqd_product_cms_pages.EmptyPage']

    def serve(self, request):

        if request.method == 'POST':
            form = KeepMeUpdatedEmailForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,
                                 _('Your data has been '
                                   'saved. We will keep '
                                   'you up to date.'))
                form = KeepMeUpdatedEmailForm()
                return render(
                    request,
                    'liqd_product_cms_pages/home_page.html', {
                        'page': self,
                        'form': form,
                    }
                )
        else:
            form = KeepMeUpdatedEmailForm()

        return render(request, 'liqd_product_cms_pages/home_page.html', {
            'page': self,
            'form': form,
        })

    content_panels = [
        ImageChooserPanel('image'),
        FieldPanel('subtitle'),
        FieldPanel('body')
    ]

    promote_panels = Page.promote_panels


class EmptyPage(Page):
    subpage_types = ['liqd_product_cms_pages.SimplePage']


class SimplePage(Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    subpage_types = ['liqd_product_cms_pages.SimplePage']
