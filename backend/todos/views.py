from django.core.serializers import serialize
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Todo
from .serializers import TodoCreateSerializer, TodoSerializer

class TodoListCreateView(generics.ListCreateAPIView):
    """ Todo 목록 조회 및 생성 API """
    queryset = Todo.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TodoCreateSerializer
        return TodoSerializer

    def list(self, request, *args, **kwargs):
        """ GET /api/todos/ - Todo 목록 조회 """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'results': serializer.data,
                'total_count': queryset.count(),
                'completed_count': queryset.filter(completed=True).count(),
            }
        )

    def create(self, request, *args, **kwargs):
        """ POST /api/todos/ - 새 Todo 생성 """
        serializer = TodoCreateSerializer(data=request.data)
        if serializer.is_valid():
            todo = serializer.save()
            return Response(
                TodoSerializer(todo).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Todo 상세 조회, 수정, 삭제 API """
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    lookup_field = 'pk'

@api_view(['PATCH'])
def todo_toggle(request, pk):
    """ PATCH /api/todos/{id}/toggle/ - Todo 완료 상태 토글 """
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()

    serializer = TodoSerializer(todo)
    return Response(serializer.data)

@api_view(['GET'])
def todo_stats(request):
    """ GET /api/todos/stats/ - Todo 통계 정보 """
    todos = Todo.objects.all()
    return Response({
        'total_count': todos.count(),
        'completed_count': todos.filter(completed=True).count(),
        'pending_count': todos.filter(completed=False).count(),
    })