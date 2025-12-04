from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Course, CalendarSlot, StudentPick, Student
from .serializers import CourseSerializer, CalendarSlotSerializer, StudentSerializer, StudentPickSerializer, RegisterSlotSerializer
from django.shortcuts import get_object_or_404

DAYS = ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]
TIMES = ["3-5", "5-7", "7-9"]

class StudentViewSet(viewsets.ModelViewSet):
    """
    Student endpoints: list, create, retrieve, update, destroy
    Admin only access
    """
    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]   # only admins can delete
        return [AllowAny()]

    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        student.delete()
        return Response({"ok": True, "message": "Student deleted successfully"}, status=status.HTTP_200_OK)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]   # only admins can delete
        return [AllowAny()]          # all other actions are public

    def perform_create(self, serializer):
        course = serializer.save()
        slots = [
            CalendarSlot(course=course, day=day, time=time, status=False, count=0)
            for day in DAYS for time in TIMES
        ]
        CalendarSlot.objects.bulk_create(slots)

    @action(detail=True, methods=['post'])
    def reset_calendar(self, request, pk=None):
        course = self.get_object()
        StudentPick.objects.filter(calendar_slot__course=course).delete()
        CalendarSlot.objects.filter(course=course).update(status=False, count=0)
        return Response({'ok': True})

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()

        student_ids = list(
            Student.objects.filter(
                student_picks__calendar_slot__course=course
            ).distinct().values_list("id", flat=True)
        )

        StudentPick.objects.filter(calendar_slot__course=course).delete()
        CalendarSlot.objects.filter(course=course).delete()
        Student.objects.filter(id__in=student_ids).delete()
        course.delete()

        return Response({"ok": True, "message": "Course and related data deleted"}, status=status.HTTP_200_OK)


class ShowCourseCalendarApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        course_serializer = CourseSerializer(course)

        slots = CalendarSlot.objects.filter(course=course)
        slots_serializer = CalendarSlotSerializer(slots, many=True)

        response_data = course_serializer.data
        response_data['calendar_slots'] = slots_serializer.data
        return Response(response_data, status=200)

class DeselectStudentSlotApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSlotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        slot_id = serializer.validated_data['calendar_slot']
        student_id = serializer.validated_data['student']

        slot = get_object_or_404(CalendarSlot, id=slot_id)
        student = get_object_or_404(Student, id=student_id)


        course = Course.objects.get(calendar_slots=slot)
        if not course:
            return Response({"message": "course is not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
        # Check if the student is actually registered
        pick = StudentPick.objects.filter(calendar_slot=slot, student=student).first()

        if not pick:
            return Response({"message": "Student is not registered in this slot"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Delete the pick
        pick_id = pick.id
        pick.delete()

        # Update slot count
        slot.count = slot.student_picks.count()
        slot.save()

        return Response(
            {
                "success": True, 
                "pick_id": pick.id,
                
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(course).data
            },
            status=status.HTTP_200_OK
        )
        

        # return Response({"success": True, "removed_pick_id": pick_id}, status=status.HTTP_200_OK)



class SelectStudentSlotApiView(APIView):
    """
    Register Selection a student in a calendar slot:
    POST /api/register-slot/
    Body: { "calendar_slot": slot_id, "student_id": student_id }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSlotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        slot_id = serializer.validated_data['calendar_slot']
        student_id = serializer.validated_data['student']

        slot = get_object_or_404(CalendarSlot, id=slot_id)
        student = get_object_or_404(Student, id=student_id)

        if not slot.status:
            return Response({"message": "Slot is not available"}, status=status.HTTP_400_BAD_REQUEST)

        if StudentPick.objects.filter(calendar_slot=slot, student=student).exists():
            return Response({"message": "Student already registered for this slot"},
                            status=status.HTTP_400_BAD_REQUEST)

        pick = StudentPick.objects.create(calendar_slot=slot, student=student)
        slot.count = slot.student_picks.count()
        slot.save()

        course = Course.objects.get(calendar_slots=slot)

        return Response(
            {
                "success": True, 
                "pick_id": pick.id,
                
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(course).data
            },
            status=status.HTTP_200_OK
        )


class ActivateSlotApiView(APIView):
    """Admin only - activate a calendar slot"""
    permission_classes = [IsAdminUser]

    def post(self, request, slot_id=None):
        slot_id = slot_id or request.data.get("slot_id") or request.query_params.get("slot_id")

        if not slot_id:
            return Response({"ok": False, "error": "slot_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        slot = get_object_or_404(CalendarSlot, id=slot_id)

        slot.status = True
        slot.save(update_fields=["status", "updated_at"])

        course = Course.objects.get(id=slot.course.id)

        return Response(
            {
                "ok": True, 
                "message": "Slot activated", 
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(slot.course).data
            },
            status=status.HTTP_200_OK
        )

class DeactivateSlotApiView(APIView):
    """Admin only - deactivate a calendar slot"""
    permission_classes = [IsAdminUser]

    def post(self, request, slot_id=None):
        slot_id = slot_id or request.data.get("slot_id") or request.query_params.get("slot_id")

        if not slot_id:
            return Response({"ok": False, "error": "slot_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        slot = get_object_or_404(CalendarSlot, id=slot_id)

        slot.status = False
        slot.save(update_fields=["status", "updated_at"])

        course = Course.objects.get(id=slot.course.id)
        return Response(
            {
                "ok": True, 
                "message": "Slot deactivated", 
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(slot.course).data
            },
            status=status.HTTP_200_OK
        )

