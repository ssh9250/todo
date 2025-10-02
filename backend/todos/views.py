from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Todo
from .serializers import (
    TodoCreateSerializer,
    TodoDetailSerializer,
    TodoListSerializer,
    TodoUpdateSerializer,
)

# mixin 패턴으로 공통 기능 분리

class TodoPagination(PageNumberPagination):
    """할 일 목록 페이지네이션 설정"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TodoViewSet(viewsets.ModelViewSet):
    """Todo CRUD 및 추가 액션을 제공하는 ViewSet"""
    pagination_class = TodoPagination
    # 필터링/검색/정렬 기능 추가 예정

    def get_queryset(self):
        """기본적으로 숨김 처리되지 않은 todo만 반환"""
        include_hidden = self.request.query_params.get('include_hidden', 'false').lower()
        base_queryset = Todo.objects.all()
        
        if include_hidden == 'true':
            return base_queryset
        return base_queryset.filter(hidden=False)

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
        """할 일 목록 조회 (성능 최적화된 통계 및 페이지네이션 포함)"""
        queryset = self.get_queryset()
        
        # 단일 쿼리로 모든 통계 계산 (성능 최적화)
        stats = queryset.aggregate(
            total_count=Count('id'),
            completed_count=Count('id', filter=Q(completed=True)),
            pending_count=Count('id', filter=Q(completed=False)),
        )
        
        # 페이지네이션 적용
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'stats': {
                    'total_count': stats['total_count'],
                    'completed_count': stats['completed_count'],
                    'pending_count': stats['pending_count'],
                }
            })
        
        # 페이지네이션이 비활성화된 경우
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'results': serializer.data,
                'total_count': stats['total_count'],
                'completed_count': stats['completed_count'],
                'pending_count': stats['pending_count'],
            }
        )
    
    @action(detail=False, methods=['get'], url_path='all')
    def list_all(self, request):
        """모든 할 일 조회 (숨김 처리된 것 포함)"""
        queryset = Todo.objects.all()
        
        # 단일 쿼리로 통계 계산 (성능 최적화)
        stats = queryset.aggregate(
            total_count=Count('id'),
            hidden_count=Count('id', filter=Q(hidden=True)),
            completed_count=Count('id', filter=Q(completed=True)),
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total_count': stats['total_count'],
            'hidden_count': stats['hidden_count'],
            'completed_count': stats['completed_count'],
            'hidden_included': True,
        })

    @action(detail=False, methods=['get'], url_path='hidden')
    def list_hidden(self, request):
        """숨김 처리된 할 일만 조회"""
        queryset = Todo.objects.filter(hidden=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total_count': queryset.count(),
        })

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
        """GET /api/todos/stats/ - 통계 정보 (성능 최적화)"""
        todos = self.get_queryset()
        
        # 단일 쿼리로 모든 통계 계산 (성능 최적화)
        stats = todos.aggregate(
            total_count=Count('id'),
            completed_count=Count('id', filter=Q(completed=True)),
            pending_count=Count('id', filter=Q(completed=False)),
        )
        
        return Response({
            'total_count': stats['total_count'],
            'completed_count': stats['completed_count'],
            'pending_count': stats['pending_count'],
        })

    @action(detail=True, methods=['patch'], url_path='hide')
    def hide(self, request, pk=None):
        """PATCH /api/todos/{id}/hide/ - 숨김 상태 토글"""
        todo = self.get_object()
        todo.hidden = not todo.hidden
        todo.save()
        serializer = TodoDetailSerializer(todo)
        return Response(serializer.data)
