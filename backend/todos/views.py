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

# mixin 패턴으로 공통 기능 분리


class TodoViewSet(viewsets.ModelViewSet):
    """Todo CRUD 및 추가 액션을 제공하는 ViewSet"""
    # 필터링/검색/정렬 기능 추가 예정

    # Query Params for filtering hidden todos
    def get_queryset(self):
        queryset = Todo.objects.all()
        
        include_hidden = self.request.query_params.get('include_hidden', 'false')
        if include_hidden == 'true':
            return queryset
        return queryset.filter(hidden=False)

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

    """쿼리 파라미터"""
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # 성능 최적화 필요 (aggregate 사용 / paginate_queryset 사용 / get_paginated_response 사용)
        stats = queryset.aggregate(
            total_count=Count('id'),
            completed_count=Count('id', filter=Q(completed=True)),
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'results': serializer.data,
                'total_count': stats['total_count'],
                'completed_count': stats['completed_count'],
            }
        )

    @action(detail=True, methods=['patch'], url_path='toggle')
    def toggle(self, request, pk=None):
        """PATCH /api/todos/{id}/toggle/ - 완료 상태 토글"""
        todo = self.get_object()
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

    @action(detail=True, methods=['patch'], url_path='hide')
    def hide(self, request, pk=None):
        todo = get_object_or_404(Todo, pk=pk)
        # todo = self.get_object()
        todo.hidden = not todo.hidden
        todo.save()
        serializer = TodoDetailSerializer(todo)
        return Response(serializer.data)
