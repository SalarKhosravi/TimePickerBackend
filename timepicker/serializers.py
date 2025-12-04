from rest_framework import serializers
from .models import Course, CalendarSlot, StudentPick, Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'created_at', 'updated_at']

class StudentPickSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), 
        source='student', 
        write_only=True
    )
    
    class Meta:
        model = StudentPick
        fields = ['id', 'student', 'student_id', 'calendar_slot', 'created_at']

class CalendarSlotSerializer(serializers.ModelSerializer):
    # include nested student picks
    student_picks = StudentPickSerializer(many=True, read_only=True)

    class Meta:
        model = CalendarSlot
        fields = ['id', 'course', 'day', 'time', 'status', 'count', 'student_picks']

class CourseSerializer(serializers.ModelSerializer):
    calendar_slots = CalendarSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'created_at', 'updated_at', 'calendar_slots']

class RegisterSlotSerializer(serializers.Serializer):
    calendar_slot = serializers.IntegerField()
    student = serializers.IntegerField()