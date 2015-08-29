from django.contrib import admin
from django_admin_bootstrapped.admin.models import SortableInline
from .models import (Weekmail, Paragraph, Article, Information)
from management.admin import PublicFileInline
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
import html.parser

class ParagraphSortable( SortableInline, admin.StackedInline):
    model = Paragraph
    extra = 0

@admin.register(Weekmail)
class WeekmailAdmin(admin.ModelAdmin):
    inlines = [ParagraphSortable, PublicFileInline,]
    actions = ['send','display',]

    def send(self, request, queryset):
        failed_weekmails = []
        for weekmail in queryset:
            if not weekmail.send():
                failed_weekmails.append(weekmail.subject)
        if failed_weekmails:
            message = _('Failed to send weekmails titled: "%s"') % \
                ('", "'.join(failed_weekmails))
        else:
            message = _('All selected weekmails have been sent.')
        self.message_user(request, message)

    def display(self, request, queryset):
        response = HttpResponse()
        html_parser = html.parser.HTMLParser()
        for weekmail in queryset:
            response.write(render_to_string('communication/display_weekmail.html',
                {'weekmail': html_parser.unescape(weekmail)}))
        return response

    send.short_description = _("Send selected weekmails")
    display.short_description = _("Display selected weekmails")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Information)
