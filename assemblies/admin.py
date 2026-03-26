from django.contrib import admin
from .models import Attendance, Question, Assembly, Agenda, DecisionOptionSet, DecisionOption

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class AgendaInline(admin.TabularInline):
    model = Agenda
    extra = 1


class DecisionOptionInline(admin.TabularInline):
    model = DecisionOption
    extra = 1


@admin.register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_at']
    inlines = [AgendaInline]


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ['title', 'assembly', 'order']
    inlines = [QuestionInline]


@admin.register(DecisionOptionSet)
class DecisionOptionSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    inlines = [DecisionOptionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'agenda', 'status', 'option_set']
    list_filter = ['status', 'agenda__assembly']
    list_editable = ['status']
    inlines = [AttendanceInline]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'question', 'registered_at', 'registered_by_admin', 'by_proxy']
    list_filter = ['question__agenda__assembly']