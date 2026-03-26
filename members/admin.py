from django.contrib import admin
from .models import Member, MembershipPeriod, DefaultPeriod


class MembershipPeriodInline(admin.TabularInline):
    model = MembershipPeriod
    extra = 1
    fields = ['membership_type', 'start_date', 'end_date']


class DefaultPeriodInline(admin.TabularInline):
    model = DefaultPeriod
    extra = 0
    fields = ['start_date', 'end_date', 'reason']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['wiki_username', 'user', 'current_membership_type', 'is_in_default']
    search_fields = ['wiki_username']
    inlines = [MembershipPeriodInline, DefaultPeriodInline]

    def current_membership_type(self, obj):
        from datetime import date
        period = obj.membership_periods.filter(
            start_date__lte=date.today()
        ).filter(
            end_date__isnull=True
        ).order_by('-start_date').first() or obj.membership_periods.filter(
            start_date__lte=date.today(),
            end_date__gte=date.today()
        ).order_by('-start_date').first()
        return period.membership_type if period else '—'
    current_membership_type.short_description = 'Membership'

    def is_in_default(self, obj):
        from datetime import date
        return obj.default_periods.filter(
            start_date__lte=date.today(),
            end_date__gte=date.today()
        ).exists()
    is_in_default.boolean = True
    is_in_default.short_description = 'In default'