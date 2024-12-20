from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from .models import User, Course, Lesson, Enrollment, LessonCompletion
from .forms import StudentSignUpForm, TeacherSignUpForm, CourseForm, LessonForm

class SignUpView(ListView):
    template_name = 'registration/signup.html'
    model = User

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            messages.success(self.request, 'Student account created successfully!')
            return redirect('student_dashboard')
        except Exception as e:
            messages.error(self.request, f'Error creating account: {str(e)}')
            return self.form_invalid(form)

class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            messages.success(self.request, 'Teacher account created successfully!')
            return redirect('teacher_dashboard')
        except Exception as e:
            messages.error(self.request, f'Error creating account: {str(e)}')
            return self.form_invalid(form)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'userprofile'):
            if user.userprofile.is_student:
                return reverse_lazy('student_dashboard')
            elif user.userprofile.is_teacher:
                return reverse_lazy('teacher_dashboard')
        return reverse_lazy('course_list')

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                course=self.object
            ).exists()
        return context

class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def test_func(self):
        return self.request.user.is_teacher
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def test_func(self):
        course = self.get_object()
        return self.request.user == course.teacher

class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('course_list')
    template_name = 'courses/course_confirm_delete.html'
    
    def test_func(self):
        course = self.get_object()
        return self.request.user == course.teacher

class LessonCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    
    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return self.request.user == course.teacher
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return context
    
    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if course.teacher != self.request.user:
            messages.error(self.request, "You don't have permission to add lessons to this course.")
            return redirect('course_detail', pk=course.pk)
        form.instance.course = course
        return super().form_valid(form)
'''
    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        form.instance.course = course
        return super().form_valid(form)
'''    

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.userprofile.is_student:
            enrollment = get_object_or_404(
                Enrollment,
                student=self.request.user,
                course=self.object.course
            )
            completion, _ = LessonCompletion.objects.get_or_create(
                enrollment=enrollment,
                lesson=self.object
            )
            context['completion'] = completion
        return context

class LessonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    
    def test_func(self):
        lesson = self.get_object()
        return self.request.user == lesson.course.teacher

class LessonDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Lesson
    template_name = 'courses/lesson_confirm_delete.html'
    
    def test_func(self):
        lesson = self.get_object()
        return self.request.user == lesson.course.teacher
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Enrollment
    template_name = 'courses/student_dashboard.html'
    context_object_name = 'enrollments'
    
    def test_func(self):
        return self.request.user.userprofile.is_student
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

class TeacherDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'courses/teacher_dashboard.html'
    context_object_name = 'courses'
    
    def test_func(self):
        return self.request.user.is_teacher
    
    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.userprofile.is_student:
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        if created:
            messages.success(request, f'You have successfully enrolled in {course.title}')
        else:
            messages.info(request, f'You are already enrolled in {course.title}')
    return redirect('course_detail', pk=course_id)

@login_required
def unenroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.userprofile.is_student:
        Enrollment.objects.filter(
            student=request.user,
            course=course
        ).delete()
        messages.success(request, f'You have successfully unenrolled from {course.title}')
    return redirect('course_detail', pk=course_id)

@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.user.userprofile.is_student:
        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=lesson.course
        )
        completion, created = LessonCompletion.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )
        if not created and not completion.is_completed:
            completion.is_completed = True
            completion.completed_at = timezone.now()
            completion.save()
            messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
    return redirect('lesson_detail', pk=lesson_id)

# Add these to views.py or create a utils.py
def is_student(user):
    return hasattr(user, 'userprofile') and user.userprofile.is_student

def is_teacher(user):
    return hasattr(user, 'userprofile') and user.userprofile.is_teacher