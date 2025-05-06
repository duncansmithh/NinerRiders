from django import forms
from .models import Room, Topic

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
