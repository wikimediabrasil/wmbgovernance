from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('<int:assembly_id>/question/<int:question_id>/vote/', views.vote, name='vote'),
    path('<int:assembly_id>/question/<int:question_id>/vote/edit/', views.edit_vote, name='edit_vote'),
    path('<int:assembly_id>/question/<int:question_id>/results/', views.results, name='results'),
    path('<int:assembly_id>/question/<int:question_id>/open/', views.open_question, name='open_question'),
    path('<int:assembly_id>/question/<int:question_id>/hang/', views.hang_question, name='hang_question'),
    path('<int:assembly_id>/question/<int:question_id>/close/', views.close_question, name='close_question'),
]