from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from django.contrib.auth import get_user_model

from timepicker.models import Course, CalendarSlot, UserPick
from timepicker.serializers import (
    CourseSerializer,
    CalendarSlotSerializer,
    RegisterSlotSerializer,
    UserSerializer,
)

User = get_user_model()

DAYS = ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]
TIMES = ["3-5", "5-7", "7-9"]


# ---------------- User ViewSet ----------------
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


# ---------------- Course ViewSet ----------------
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        course = serializer.save()
        # create calendar slots for all days and times
        slots = [
            CalendarSlot(course=course, day=day, time=time, status=True, count=0)
            for day in DAYS
            for time in TIMES
        ]
        CalendarSlot.objects.bulk_create(slots)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reset_calendar(self, request, pk=None):
        course = self.get_object()
        # delete all picks and reset slots
        UserPick.objects.filter(calendar_slot__course=course).delete()
        CalendarSlot.objects.filter(course=course).update(status=False, count=0)
        return Response({"ok": True})


# ---------------- Show Calendar ----------------
class ShowCourseCalendarApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_id):
        course = get_object_or_404(
            Course.objects.prefetch_related("calendar_slots__user_picks__user"),
            id=course_id,
        )
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------- Register / Deselect Slot ----------------
class SelectSlotApiView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slot_id = serializer.validated_data["calendar_slot"]
        slot = get_object_or_404(CalendarSlot, id=slot_id)

        if not slot.status:
            return Response(
                {"message": "Slot is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if UserPick.objects.filter(calendar_slot=slot, user=request.user).exists():
            return Response(
                {"message": "User already registered for this slot"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # create pick
        UserPick.objects.create(calendar_slot=slot, user=request.user)

        # update count
        slot.count = slot.user_picks.count()
        slot.save(update_fields=["count", "updated_at"])

        return Response(
            {
                "success": True,
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(slot.course).data,
            },
            status=status.HTTP_200_OK,
        )


class DeselectSlotApiView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slot_id = serializer.validated_data["calendar_slot"]
        slot = get_object_or_404(CalendarSlot, id=slot_id)

        pick = UserPick.objects.filter(calendar_slot=slot, user=request.user).first()

        if not pick:
            return Response(
                {"message": "User is not registered in this slot"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pick.delete()

        slot.count = slot.user_picks.count()
        slot.save(update_fields=["count", "updated_at"])

        return Response(
            {
                "success": True,
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(slot.course).data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------- Activate / Deactivate Slot ----------------
class ActivateSlotApiView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slot_id=None):
        slot_id = slot_id or request.data.get("slot_id")
        if not slot_id:
            return Response(
                {"error": "slot_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        slot = get_object_or_404(CalendarSlot, id=slot_id)
        slot.status = True
        slot.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "ok": True,
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(slot.course).data,
            },
            status=status.HTTP_200_OK,
        )


class DeactivateSlotApiView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slot_id=None):
        slot_id = slot_id or request.data.get("slot_id")
        if not slot_id:
            return Response(
                {"error": "slot_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        slot = get_object_or_404(CalendarSlot, id=slot_id)
        slot.status = False
        slot.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "ok": True,
                "slot": CalendarSlotSerializer(slot).data,
                "course": CourseSerializer(slot.course).data,
            },
            status=status.HTTP_200_OK,
        )
