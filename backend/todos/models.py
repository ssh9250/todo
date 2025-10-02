from django.db import models
from django.utils import timezone


class Todo(models.Model):
    title = models.CharField(max_length=20, verbose_name='제목', default='제목을 입력하세요.')
    description = models.TextField(blank=True, null=True, verbose_name='설명')
    completed = models.BooleanField(default=False, verbose_name='완료 여부')
    hidden = models.BooleanField(default=False, verbose_name='숨김 여부')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '할 일'
        verbose_name_plural = '할 일 목록'
        ordering = ['-created_at']

    def __str__(self):
        return self.title