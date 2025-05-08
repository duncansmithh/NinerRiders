from django import forms
from .models import Room, Topic
from django.forms import ModelForm, Select
from .models import ClassSchedule, Day
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
import datetime

class RoomForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(name__in=['Requested', 'Scheduled']),
        empty_label="Select Ride Type",
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class ClassScheduleForm(forms.ModelForm):
    days = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ClassSchedule
        fields = ['course_name', 'days', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        time_choices = [
            (datetime.time(hour, minute).strftime("%H:%M"), 
             datetime.time(hour, minute).strftime("%I:%M %p"))
            for hour in range(0, 24)
            for minute in range(0, 60, 5)
        ]
        self.fields['start_time'].widget = forms.Select(choices=time_choices)
        self.fields['end_time'].widget = forms.Select(choices=time_choices)

class CustomUserCreationForm(UserCreationForm):
    student_id = forms.CharField(
        max_length=9,
        label='UNC Charlotte Student ID'
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if not re.match(r'^8\d{8}$', student_id):
            raise forms.ValidationError("Enter a valid UNC Charlotte Student ID")
        return student_id