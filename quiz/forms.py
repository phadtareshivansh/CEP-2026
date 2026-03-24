from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, ForumPost, MentorRequest

class QuizAnswerForm(forms.Form):
    """Form to handle quiz answers"""
    question_id = forms.IntegerField(widget=forms.HiddenInput())
    answer = forms.ChoiceField(choices=[(0, 'No'), (1, 'Yes')], widget=forms.HiddenInput())


class SignUpForm(UserCreationForm):
    """User registration form with additional fields"""
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].split('@')[0]
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class LoginForm(forms.Form):
    """User login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    bio = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about yourself...'
        }),
        required=False
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, Country'
        }),
        required=False
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number'
        }),
        required=False
    )
    current_role = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current role/position'
        }),
        required=False
    )
    experience_level = forms.ChoiceField(
        choices=UserProfile._meta.get_field('experience_level').choices,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'phone', 'current_role', 'experience_level', 'profile_picture']


class ForumPostForm(forms.ModelForm):
    """Forum post creation form"""
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Post title'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Share your thoughts, questions, or experiences...'
        })
    )

    class Meta:
        model = ForumPost
        fields = ['category', 'career', 'title', 'content']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'career': forms.Select(attrs={'class': 'form-select'}),
        }


class MentorRequestForm(forms.ModelForm):
    """Mentor request form"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell the mentor about yourself and why you want mentorship...'
        })
    )
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False
    )
    scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        required=False
    )

    class Meta:
        model = MentorRequest
        fields = ['message', 'scheduled_date', 'scheduled_time']


class CareerSearchForm(forms.Form):
    """Advanced career search form"""
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search careers...'
        }),
        required=False
    )
    category = forms.ChoiceField(
        choices=[
            ('', 'All Categories'),
            ('Realistic', 'Realistic'),
            ('Investigative', 'Investigative'),
            ('Artistic', 'Artistic'),
            ('Social', 'Social'),
            ('Enterprising', 'Enterprising'),
            ('Conventional', 'Conventional'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False
    )


class JobSearchForm(forms.Form):
    """Job listings search form"""
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title or company'
        }),
        required=False
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, Country'
        }),
        required=False
    )


class MentorSearchForm(forms.Form):
    """Find mentors form"""
    specialization = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Field of expertise'
        }),
        required=False
    )
