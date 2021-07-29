from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from records.models import *
from django.utils.translation import gettext_lazy as _
# Register your models here.


class CustomUserAdmin(UserAdmin):
    # Add additional is_teacher field to user edit form in admin
    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_teacher')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name',
                                         'birth_date', 'address', 'zip_code',
                                         'city', 'phone', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Add required fields to user creation form in admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('School records'), {'fields': ('is_teacher',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'birth_date',
                                         'address', 'zip_code', 'city',
                                         'phone', 'email')}),
    )

    list_display = UserAdmin.list_display + \
        ('is_teacher', 'is_educator', 'student_group')
    list_filter = UserAdmin.list_filter + ('is_teacher',)
    ordering = ('last_name',)


class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'educator')
    search_fields = ('name', 'educator__first_name', 'educator__last_name')


class StudentGroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'date_start', 'date_end')
    search_fields = ('student__first_name',
                     'student__last_name', 'group__name')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')
    search_fields = ('name', 'group__name')


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'get_group', 'teacher',
                    'date_start', 'date_end', 'day_of_week', 'period')
    search_fields = ('name', 'course__group__name',
                     'teacher__first_name', 'teacher__last_name')

    def get_group(self, obj):
        return obj.course.group


class LessonAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'short_subject',
                    'get_course', 'get_group', 'get_teacher')

    def get_course(self, obj):
        return obj.schedule.course

    def get_group(self, obj):
        return obj.schedule.course.group

    def get_teacher(self, obj):
        return obj.schedule.teacher


admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(StudentGroupAssignment, StudentGroupAssignmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Period)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Attendance)
