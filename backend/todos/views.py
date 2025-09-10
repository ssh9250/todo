from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Todo

def todo_list(request):
    todos = Todo.objects.all()
    context = {
        'todos': todos,
        'total_count': todos.count(),
        'completed_count': todos.filter(completed=True).count(),
    }
    return render(request, 'todos/todo_list.html', context)

def todo_detail(request, pk):
    todo = get_object_or_404(Todo, pk=pk)# 404 에러 발생 시 404 페이지 반환
    context = {
        'todo': todo,
    }
    return render(request, 'todos/todo_detail.html', context)

def todo_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if title:
            Todo.objects.create(
                title=title,
                description=description,
            )
            return redirect('todo_list')

    return render(request, 'todos/todo_create.html')

def todo_toggle(request, pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=pk)
        
