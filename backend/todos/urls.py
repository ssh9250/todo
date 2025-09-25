from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TodoViewSet

router = DefaultRouter()
router.register('', TodoViewSet, basename='todo')

urlpatterns = [
    path('', include(router.urls)),
]


'''
urlpatterns = [
    path('', views.TodoListCreateView.as_view(), name='todo-list-create'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name = 'todo-detail'),
    path('<int:pk>/toggle/', views.todo_toggle, name = 'todo-toggle'),
    path('stats/', views.todo_stats, name = 'todo-stats'),

]

urlpatterns = [
    path('', TodoViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', TodoViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    })),
    path('<int:pk>/toggle/', TodoViewSet.as_view({'patch': 'toggle'})),
    path('stats/', TodoViewSet.as_view({'get': 'stats'})),
]
'''