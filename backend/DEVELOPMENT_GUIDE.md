# Todo 백엔드 개발 가이드

## 프로젝트 개요
Django REST Framework를 사용한 Todo 애플리케이션 백엔드 개발 과정을 문서화합니다.

## 개발 환경 설정

### 1. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 2. Django 및 필수 패키지 설치
```bash
# requirements.txt 생성
echo "Django==5.2.6" > requirements.txt
echo "djangorestframework==3.16.1" >> requirements.txt
echo "django-cors-headers==4.9.0" >> requirements.txt

# 패키지 설치
pip install -r requirements.txt
```

### 3. Django 프로젝트 생성
```bash
# 프로젝트 생성
django-admin startproject todo .

# 앱 생성
python manage.py startapp todos
```

## 프로젝트 구조
```
backend/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── todo/                    # 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── todos/                   # Todo 앱
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── tests.py
    └── migrations/
        └── __init__.py
```

## 데이터베이스 모델 설계

### Todo 모델 (`todos/models.py`)
```python
from django.db import models
from django.utils import timezone

class Todo(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목', default='제목을 입력하세요.')
    description = models.TextField(blank=True, null=True, verbose_name='설명')
    completed = models.BooleanField(default=False, verbose_name='완료 여부')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '할 일'
        verbose_name_plural = '할 일 목록'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

### 모델 특징
- **title**: 최대 200자 제목 필드
- **description**: 선택적 설명 필드
- **completed**: 완료 상태를 나타내는 불린 필드
- **created_at**: 생성 시간 (기본값: 현재 시간)
- **updated_at**: 수정 시간 (자동 업데이트)
- **정렬**: 생성일 기준 내림차순

## 데이터베이스 마이그레이션

### 1. 마이그레이션 파일 생성
```bash
python manage.py makemigrations todos
```

### 2. 마이그레이션 적용
```bash
python manage.py migrate
```

## Django 설정

### settings.py 주요 설정
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',           # DRF 추가
    'corsheaders',              # CORS 헤더 추가
    'todos',                    # Todo 앱 추가
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS 미들웨어 추가
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React 개발 서버
    "http://127.0.0.1:3000",
]

# DRF 설정
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
```

## Serializer 설계 및 개선

### 초기 설계 (단일 Serializer)
```python
# 초기 TodoSerializer (예상)
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = '__all__'
```

### 개선된 설계 (역할별 Serializer)

#### BaseTodoSerializer
```python
class BaseTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = []

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("제목은 필수입니다.")
        return value.strip()
```

#### 목록용 Serializer
```python
class TodoListSerializer(BaseTodoSerializer):
    """목록 조회용 경량 Serializer"""
    class Meta:
        model = Todo
        fields = ['id', 'title', 'completed', 'created_at']
```

#### 상세용 Serializer
```python
class TodoDetailSerializer(BaseTodoSerializer):
    """상세 조회용 전체 Serializer"""
    class Meta:
        model = Todo
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

#### 생성용 Serializer
```python
class TodoCreateSerializer(BaseTodoSerializer):
    """생성용 Serializer"""
    class Meta:
        model = Todo
        fields = ['title', 'description']

    def validate_title(self, value):
        value = super().validate_title(value)
        if len(value.strip()) > 100:
            raise serializers.ValidationError("제목은 100자를 초과할 수 없습니다.")
        return value
    
    def create(self, validated_data):
        return Todo.objects.create(**validated_data)
```

#### 수정용 Serializer
```python
class TodoUpdateSerializer(BaseTodoSerializer):
    """수정용 Serializer"""
    class Meta:
        model = Todo
        fields = ['title', 'description', 'completed']

    def validate_title(self, value):
        value = super().validate_title(value)
        if len(value.strip()) > 100:
            raise serializers.ValidationError("제목은 100자를 초과할 수 없습니다.")
        return value.strip() if value else value

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()
        return instance
```

### Serializer 설계 개선 이유
1. **응답 최적화**: 목록 조회 시 불필요한 필드 제외로 네트워크 트래픽 감소
2. **검증 일관성**: 각 목적별로 적절한 검증 로직 적용
3. **유지보수성**: 요구사항 변경 시 영향 범위 최소화
4. **보안**: read_only_fields로 서버 관리 필드 보호

## View 설계 및 개선

### 초기 설계 (Generic Views + Function Views)
```python
# 초기 설계 (예상)
class TodoListCreateView(generics.ListCreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

@api_view(['PATCH'])
def todo_toggle(request, pk):
    # 토글 로직

@api_view(['GET'])
def todo_stats(request):
    # 통계 로직
```

### 개선된 설계 (ViewSet 기반)

#### TodoViewSet
```python
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
        """목록 조회 (통계 정보 포함)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total_count': queryset.count(),
            'completed_count': queryset.filter(completed=True).count(),
        })

    @action(detail=True, methods=['patch'], url_path='toggle')
    def toggle(self, request, pk=None):
        """완료 상태 토글"""
        todo = get_object_or_404(Todo, pk=pk)
        todo.completed = not todo.completed
        todo.save()
        serializer = TodoDetailSerializer(todo)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """통계 정보 조회"""
        todos = self.get_queryset()
        return Response({
            'total_count': todos.count(),
            'completed_count': todos.filter(completed=True).count(),
            'pending_count': todos.filter(completed=False).count(),
        })
```

### ViewSet 설계 개선 이유
1. **응집도**: CRUD와 커스텀 액션을 한 곳에 집약
2. **일관성**: 권한, 로깅, 스로틀링 정책을 통일적으로 적용 가능
3. **확장성**: 새로운 액션 추가가 용이
4. **라우팅 단순화**: Router가 URL 패턴 자동 생성

## URL 라우팅 설계

### 초기 설계 (수동 URL 패턴)
```python
# todos/urls.py (초기)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.TodoListCreateView.as_view(), name='todo-list-create'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='todo-detail'),
    path('<int:pk>/toggle/', views.todo_toggle, name='todo-toggle'),
    path('stats/', views.todo_stats, name='todo-stats'),
]
```

### 개선된 설계 (DRF Router)
```python
# todos/urls.py (개선)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet

router = DefaultRouter()
router.register('', TodoViewSet, basename='todo')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 프로젝트 URL 설정
```python
# todo/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/todos/', include('todos.urls')),
]
```

### Router 기반 설계 개선 이유
1. **자동화**: CRUD URL 패턴 자동 생성
2. **표준화**: RESTful URL 패턴 보장
3. **유지보수**: URL 패턴 관리 부담 감소
4. **확장성**: 새로운 ViewSet 추가 시 자동 라우팅

## API 엔드포인트

### 자동 생성된 URL 패턴
```
GET    /api/todos/           # 목록 조회
POST   /api/todos/           # 생성
GET    /api/todos/{id}/      # 상세 조회
PUT    /api/todos/{id}/      # 전체 수정
PATCH  /api/todos/{id}/      # 부분 수정
DELETE /api/todos/{id}/      # 삭제
PATCH  /api/todos/{id}/toggle/  # 완료 상태 토글
GET    /api/todos/stats/     # 통계 조회
```

### 응답 예시

#### 목록 조회 응답
```json
{
  "results": [
    {
      "id": 1,
      "title": "할 일 1",
      "completed": false,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total_count": 1,
  "completed_count": 0
}
```

#### 통계 조회 응답
```json
{
  "total_count": 10,
  "completed_count": 3,
  "pending_count": 7
}
```

## 개발 과정에서의 주요 개선사항

### 1. Serializer 오타 수정
- `field` → `fields`
- `read_only_field` → `read_only_fields`
- `validated_title` → `validate_title`

### 2. 설계 패턴 개선
- **단일 Serializer** → **역할별 Serializer**
- **Generic Views + FBV** → **ViewSet 기반**
- **수동 URL 패턴** → **DRF Router**

### 3. 성능 최적화
- 목록 조회 시 필드 최소화
- 통계 정보를 목록 응답에 포함

## 테스트 및 실행

### 개발 서버 실행
```bash
python manage.py runserver
```

### 관리자 페이지 접근
```bash
# 슈퍼유저 생성
python manage.py createsuperuser

# 관리자 페이지: http://127.0.0.1:8000/admin/
```

### API 테스트
```bash
# 목록 조회
curl http://127.0.0.1:8000/api/todos/

# 생성
curl -X POST http://127.0.0.1:8000/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "새 할 일", "description": "설명"}'

# 토글
curl -X PATCH http://127.0.0.1:8000/api/todos/1/toggle/

# 통계
curl http://127.0.0.1:8000/api/todos/stats/
```

## 향후 개선 방향

### 1. 페이지네이션
- 표준 DRF 페이지네이션 적용
- `PageNumberPagination` 또는 `LimitOffsetPagination` 사용

### 2. 검증 로직 개선
- 공통 검증 메서드를 BaseTodoSerializer로 이동
- 제목 길이 제한을 모델 필드와 일치시키기

### 3. 캐싱
- 통계 정보에 짧은 TTL 캐시 적용
- Redis 또는 메모리 캐시 활용

### 4. 인증/권한
- JWT 토큰 기반 인증
- 사용자별 Todo 관리

### 5. API 문서화
- DRF의 자동 문서화 기능 활용
- Swagger/OpenAPI 스펙 생성

## 결론

Django REST Framework를 사용한 Todo 백엔드 개발을 통해 다음과 같은 학습을 진행했습니다:

1. **모델 설계**: Django ORM을 활용한 데이터베이스 모델링
2. **Serializer 설계**: 역할별 Serializer로 응답 최적화 및 검증 분리
3. **ViewSet 패턴**: CRUD와 커스텀 액션을 통합한 RESTful API 설계
4. **Router 활용**: 자동 URL 패턴 생성으로 라우팅 단순화
5. **설계 개선**: 초기 설계에서 확장 가능한 구조로 리팩터링

이러한 과정을 통해 Django의 모범 사례를 학습하고, 확장 가능하고 유지보수하기 쉬운 백엔드 구조를 구축할 수 있었습니다.
