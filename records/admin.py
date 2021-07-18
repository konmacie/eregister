from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from records.models import User, StudentGroup, StudentGroupAssignment
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


admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(StudentGroupAssignment, StudentGroupAssignmentAdmin)
