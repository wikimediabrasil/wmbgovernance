from django.contrib import admin
from .models import Proxy, Vote


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ['assembly', 'grantor', 'grantee']
    list_filter = ['assembly']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['question', 'voter', 'option', 'proxy', 'cast_at']
    list_filter = ['question__agenda__assembly', 'question']
    readonly_fields = ['cast_at']