import os, shutil, random, string
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from timepicker.models import Course, CalendarSlot, UserPick


class Command(BaseCommand):
    help = "Seed the database with initial data and reset DB."

    def handle(self, *args, **options):
        stdout = self.stdout

        # ---------- Remove SQLite DB ----------
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
            stdout.write(self.style.SUCCESS('DB removed successfully.'))
        else:
            stdout.write('DB does not exist.')

        # ---------- Remove old migrations ----------
        migrations_path = os.path.join(settings.BASE_DIR, 'timepicker', 'migrations')
        for filename in os.listdir(migrations_path):
            file_path = os.path.join(migrations_path, filename)
            try:
                if filename == '__init__.py':
                    continue
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                stdout.write(f"Error deleting {file_path}: {e}")

        # ---------- Recreate migrations ----------
        try:
            call_command('makemigrations', interactive=True)
            call_command('migrate', interactive=True)
            stdout.write(self.style.SUCCESS('Migrations applied'))
        except Exception as e:
            stdout.write(self.style.ERROR(f'Migration Failed: {e}'))

        # === Flush DB just to be sure ===
        self.stdout.write(self.style.WARNING("Flushing database..."))
        call_command("flush", "--noinput")

        # === Admin setup ===
        self.stdout.write("Creating groups...")
        groups_info = {"Admin": "full"}
        for group_name in groups_info:
            Group.objects.get_or_create(name=group_name)

        self.stdout.write("Creating admin user...")
        User = get_user_model()
        admin_user, created = User.objects.get_or_create(username="01234567890")
        if created:
            admin_user.full_name = "Admin User"
            admin_user.set_password("Admin@123")  # strong password
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Admin user created."))
        else:
            self.stdout.write("Admin user already exists.")

        # === Create Courses ===
        self.stdout.write("Creating courses...")
        courses_data = [
            {"title": "Python Course"},
            {"title": "Web Design Course"},
        ]
        courses = []
        for data in courses_data:
            course, _ = Course.objects.get_or_create(**data)
            courses.append(course)
        self.stdout.write(self.style.SUCCESS("Courses created."))

        # === Create CalendarSlots ===
        days = ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]
        times = ["3-5", "5-7", "7-9"]

        for course in courses:
            for day in days:
                for time in times:
                    status = random.choice([True, True, True, False])
                    CalendarSlot.objects.create(
                        course=course,
                        day=day,
                        time=time,
                        status=status,
                        count=0,
                    )
        self.stdout.write(self.style.SUCCESS("Calendar slots created successfully."))

        # === Create regular users ===
        self.stdout.write("Creating users...")
        users_data = [
            {"phone": "09991112222", "full_name": "Ali Ahmadi"},
            {"phone": "09992223333", "full_name": "Sara Mohammadi"},
            {"phone": "09993334444", "full_name": "Reza Hosseini"},
            {"phone": "09994445555", "full_name": "Zahra Karimi"},
        ]
        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(username=data["phone"])
            if created:
                user.full_name = data["full_name"]
                # random strong password 8 chars with letters, numbers, symbols
                password = 'Admin@123'
                user.set_password(password)
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS("Users created."))

        # === Create UserPicks ===
        self.stdout.write("Creating user picks...")
        available_slots = CalendarSlot.objects.filter(status=True)

        for user in users:
            num_picks = random.randint(2, 3)
            selected_slots = random.sample(list(available_slots), min(num_picks, len(available_slots)))
            for slot in selected_slots:
                if not UserPick.objects.filter(user=user, calendar_slot=slot).exists():
                    UserPick.objects.create(user=user, calendar_slot=slot)
                    slot.count = slot.user_picks.count()
                    slot.save()

        self.stdout.write(self.style.SUCCESS("User picks created successfully."))
        self.stdout.write(self.style.SUCCESS("✅ Seeding complete!"))
