from django.urls import path
from rest_framework.routers import DefaultRouter
from timepicker.views import (
    UserViewSet,
    CourseViewSet,
    ShowCourseCalendarApiView,
    SelectSlotApiView,
    DeselectSlotApiView,
    ActivateSlotApiView,
    DeactivateSlotApiView,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path(
        'course/calendar/<int:course_id>/',
        ShowCourseCalendarApiView.as_view(),
        name='show_calendar_api'
    ),
    path(
        'register-slot/select/',
        SelectSlotApiView.as_view(),
        name='select_slot_api'
    ),
    path(
        'register-slot/deselect/',
        DeselectSlotApiView.as_view(),
        name='deselect_slot_api'
    ),
    path(
        'slots/<int:slot_id>/activate/',
        ActivateSlotApiView.as_view(),
        name='activate_slot_api'
    ),
    path(
        'slots/<int:slot_id>/deactivate/',
        DeactivateSlotApiView.as_view(),
        name='deactivate_slot_api'
    ),
] + router.urls
