from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Course, Lesson, Enrollment, LessonCompletion

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')

    def get_user_type(self, obj):
        try:
            if obj.userprofile.is_student and  obj.userprofile.is_teacher:
                return 'Student, Teacher'
            if obj.userprofile.is_student:
                return 'Student'
            elif obj.userprofile.is_teacher:
                return 'Teacher'
            return 'N/A'
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_user_type.short_description = 'User Type'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'teacher__username')
    list_filter = ('created_at', 'updated_at')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    ordering = ('course', 'order', 'created_at')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date_enrolled', 'last_accessed')
    list_filter = ('date_enrolled', 'last_accessed')
    search_fields = ('student__username', 'course__title')

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('enrollment__student__username', 'lesson__title')