from rest_framework import serializers
from django.contrib.auth import get_user_model
from timepicker.models import Course, CalendarSlot, UserPick

User = get_user_model()

# Serializer for User
class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'email', 'is_active', 'is_staff']
        read_only_fields = fields



class UserPickSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserPick
        fields = [
            "id",
            "user",
            "calendar_slot",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.get_username(),
            "full_name": obj.user.full_name,
            "email": obj.user.email,
            "is_active": obj.user.is_active,
        }

class CalendarSlotSerializer(serializers.ModelSerializer):
    user_picks = UserPickSerializer(many=True, read_only=True)

    class Meta:
        model = CalendarSlot
        fields = [
            'id',
            'course',
            'day',
            'time',
            'status',
            'count',
            'user_picks',
        ]


class CourseSerializer(serializers.ModelSerializer):
    calendar_slots = CalendarSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'created_at',
            'updated_at',
            'calendar_slots',
        ]


class RegisterSlotSerializer(serializers.Serializer):
    calendar_slot = serializers.IntegerField()
