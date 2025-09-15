from rest_framework import serializers
from .models import Todo


class TodoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("제목은 필수입니다.")
        return value.strip()

    def create(self, validated_data):
        """
        Custom create method
        """
        return Todo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Custom update method
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()
        return instance


class TodoListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for list views
    """

    class Meta:
        model = Todo
        fields = ['id', 'title', 'completed', 'created_at']


class TodoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Todo
        fields = ['title', 'description']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("제목은 필수입니다.")
        if len(value.strip()) > 100:
            raise serializers.ValidationError("제목은 100자를 초과할 수 없습니다.")
        return value.strip()


class TodoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing todos
    """

    class Meta:
        model = Todo
        fields = ['title', 'description', 'completed']

    def validate_title(self, value):
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip() if value else value