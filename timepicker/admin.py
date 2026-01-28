from django.contrib import admin
from django.contrib.auth import get_user_model
from timepicker.models import Course, CalendarSlot, UserPick

User = get_user_model()

# ---------- Inlines ----------

class UserPickInlineForUser(admin.TabularInline):
    model = UserPick
    extra = 0
    readonly_fields = ("calendar_slot", "created_at", "updated_at")
    autocomplete_fields = ("calendar_slot",)


class UserPickInlineForCalendarSlot(admin.TabularInline):
    model = UserPick
    extra = 0
    readonly_fields = ("user", "created_at", "updated_at")
    autocomplete_fields = ("user",)



# ---------- User Admin (attach picks to user) ----------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "username", "is_active", "is_staff")
    search_fields = ("full_name", "username")
    ordering = ("id",)
    inlines = [UserPickInlineForUser]


# ---------- Course Admin ----------

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")
    search_fields = ("title",)
    ordering = ("-created_at",)


# ---------- CalendarSlot Admin ----------

@admin.register(CalendarSlot)
class CalendarSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id", "course", "day", "time", "status", "count", "created_at", "updated_at"
    )
    list_editable = ("status",)
    list_filter = ("day", "status", "course")
    search_fields = ("course__title",)
    ordering = ("day_order", "time")
    inlines = [UserPickInlineForCalendarSlot]

# ---------- UserPick Admin ----------

@admin.register(UserPick)
class UserPickAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "calendar_slot", "created_at")
    list_filter = ("calendar_slot__day", "calendar_slot__course")
    search_fields = ("user__username", "user__full_name")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "calendar_slot")