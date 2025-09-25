from rest_framework import serializers
from .models import Todo

class BaseTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = []

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("제목은 필수입니다.")
        return value.strip()


class TodoListSerializer(BaseTodoSerializer):
    """
    Simplified serializer for list views
    """

    class Meta:
        model = Todo
        fields = ['id', 'title', 'completed', 'created_at']


class TodoDetailSerializer(BaseTodoSerializer):
    
    class Meta:
        model = Todo
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TodoCreateSerializer(BaseTodoSerializer):

    class Meta:
        model = Todo
        fields = ['title', 'description']

    def validate_title(self, value):
        value = super().validate_title(value)

        if len(value.strip()) > 100:
            raise serializers.ValidationError("제목은 100자를 초과할 수 없습니다.")

        return value
    
    def create(self, validated_data):
        """
        Custom create method
        """
        return Todo.objects.create(**validated_data)


class TodoUpdateSerializer(BaseTodoSerializer):
    """
    Serializer for updating existing todos
    """

    class Meta:
        model = Todo
        fields = ['title', 'description', 'completed']

    def validate_title(self, value):
        value = super().validate_title(value)

        if len(value.strip()) > 100:
            raise serializers.ValidationError("제목은 100자를 초과할 수 없습니다.")

        return value.strip() if value else value

    def update(self, instance, validated_data):
        """
        Custom update method
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()
        return instance