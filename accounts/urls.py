from django.urls import path, include
from accounts import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.login_oauth, name='login'),
    path('logout/', views.logout_oauth, name='logout'),
    path('forbidden/', views.login_forbidden, name='forbidden'),
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
]
