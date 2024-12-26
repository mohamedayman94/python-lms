# courses/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from ckeditor.widgets import CKEditorWidget
from .models import User, Course, Lesson


class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
            user.userprofile.is_student = True
            user.userprofile.save()
        return user

class TeacherSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
            user.userprofile.is_teacher = True
            user.userprofile.save()
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'image']
        widgets = {
            'description': CKEditorWidget(),
        }
        
def clean_title(self):
    title = self.cleaned_data.get('title')
    if Course.objects.filter(title=title).exists():
        raise forms.ValidationError("A course with this title already exists.")
    return title        

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_embed_code', 'image', 'order']
        widgets = {
            'content': CKEditorWidget(),
            'video_embed_code': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Paste your video embed code here (e.g., <iframe>...</iframe>)'
            }),
            'order': forms.NumberInput(attrs={'min': 0}),
        }