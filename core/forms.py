from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import (
    CreatorProfile, ContentIdea, PlannerEntry, SupportTicket,
    NICHE_CHOICES, FORMAT_CHOICES, GOAL_CHOICES, TONE_CHOICES,
    EXPERIENCE_CHOICES, PLANNER_STATUS_CHOICES, PRIORITY_CHOICES,
    TICKET_STATUS_CHOICES
)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password (min 8 characters)'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class CreatorOnboardingForm(forms.ModelForm):
    class Meta:
        model = CreatorProfile
        fields = [
            'display_name', 'instagram_handle', 'niche',
            'target_audience', 'content_goals', 'preferred_formats',
            'preferred_tone', 'experience_level', 'bio'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Creator / Brand Name'}),
            'instagram_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@yourhandle'}),
            'niche': forms.Select(attrs={'class': 'form-select'}),
            'target_audience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Busy moms wanting fast 15-min dinners'}),
            'content_goals': forms.Select(choices=GOAL_CHOICES, attrs={'class': 'form-select'}),
            'preferred_formats': forms.Select(choices=FORMAT_CHOICES, attrs={'class': 'form-select'}),
            'preferred_tone': forms.Select(choices=TONE_CHOICES, attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description of your creator journey'}),
        }


class CreatorProfileForm(forms.ModelForm):
    class Meta:
        model = CreatorProfile
        fields = [
            'display_name', 'instagram_handle', 'niche',
            'target_audience', 'content_goals', 'preferred_formats',
            'preferred_tone', 'experience_level', 'bio'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_handle': forms.TextInput(attrs={'class': 'form-control'}),
            'niche': forms.Select(attrs={'class': 'form-select'}),
            'target_audience': forms.TextInput(attrs={'class': 'form-control'}),
            'content_goals': forms.Select(choices=GOAL_CHOICES, attrs={'class': 'form-select'}),
            'preferred_formats': forms.Select(choices=FORMAT_CHOICES, attrs={'class': 'form-select'}),
            'preferred_tone': forms.Select(choices=TONE_CHOICES, attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class IdeaGeneratorForm(forms.Form):
    niche = forms.ChoiceField(choices=NICHE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    format_type = forms.ChoiceField(choices=FORMAT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    content_goal = forms.ChoiceField(choices=GOAL_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    tone = forms.ChoiceField(choices=TONE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    topic = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specific keyword or topic (e.g. morning routine, barrier repair)'})
    )
    target_audience = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to use profile default'})
    )


class ContentIdeaEditForm(forms.ModelForm):
    class Meta:
        model = ContentIdea
        fields = [
            'title', 'hook', 'main_concept', 'objective',
            'content_outline', 'visual_direction', 'caption',
            'hashtags', 'call_to_action', 'filming_editing_tips'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'hook': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'main_concept': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'content_outline': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 5}),
            'visual_direction': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'caption': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 6}),
            'hashtags': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'call_to_action': forms.TextInput(attrs={'class': 'form-control'}),
            'filming_editing_tips': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PlannerEntryForm(forms.ModelForm):
    class Meta:
        model = PlannerEntry
        fields = ['title', 'format_type', 'scheduled_date', 'scheduled_time', 'status', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title or concept'}),
            'format_type': forms.Select(choices=FORMAT_CHOICES, attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(choices=PLANNER_STATUS_CHOICES, attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Filming location, props, caption notes...'}),
        }


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'description', 'priority', 'related_error_code', 'guest_name', 'guest_email']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of the issue'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what happened and any steps to reproduce'}),
            'priority': forms.Select(choices=PRIORITY_CHOICES, attrs={'class': 'form-select'}),
            'related_error_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS-AUTH-001 (optional)'}),
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
        }
