from rest_framework import serializers
from django.contrib.auth import get_user_model
from timepicker.models import Course, CalendarSlot, UserPick
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

# Serializer for User
class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'email', 'is_active', 'is_staff']
        read_only_fields = fields


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ['full_name', 'username', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            full_name=validated_data['full_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)



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
