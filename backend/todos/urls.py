from django.urls import path
from . import views

urlpatterns = [
    path('', views.TodoListCreateView.as_view(), name='todo-list-create'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name = 'todo-detail'),
    path('<int:pk>/toggle/', views.todo_toggle, name = 'todo-toggle'),
    path('stats/', views.todo_stats, name = 'todo-stats'),

]