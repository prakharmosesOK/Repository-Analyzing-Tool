from django.urls import path
from . import views

# URL Conf
urlpatterns = [
    path('get_dependencies/', views.get_dependencies, name='get_dependencies'),
    path('get_commit_history/', views.get_commit_history, name='get_commit_history'),
]