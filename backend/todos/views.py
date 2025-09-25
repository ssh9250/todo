from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Todo
from .serializers import (
    TodoCreateSerializer,
    TodoDetailSerializer,
    TodoListSerializer,
    TodoUpdateSerializer,
)


class TodoViewSet(viewsets.ModelViewSet):
    """Todo CRUD 및 추가 액션을 제공하는 ViewSet"""

    queryset = Todo.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TodoListSerializer
        if self.action == 'retrieve':
            return TodoDetailSerializer
        if self.action == 'create':
            return TodoCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TodoUpdateSerializer
        return TodoDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'results': serializer.data,
                'total_count': queryset.count(),
                'completed_count': queryset.filter(completed=True).count(),
            }
        )

    @action(detail=True, methods=['patch'], url_path='toggle')
    def toggle(self, request, pk=None):
        """PATCH /api/todos/{id}/toggle/ - 완료 상태 토글"""
        todo = get_object_or_404(Todo, pk=pk)
        todo.completed = not todo.completed
        todo.save()
        serializer = TodoDetailSerializer(todo)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """GET /api/todos/stats/ - 통계 정보"""
        todos = self.get_queryset()
        return Response({
            'total_count': todos.count(),
            'completed_count': todos.filter(completed=True).count(),
            'pending_count': todos.filter(completed=False).count(),
        })