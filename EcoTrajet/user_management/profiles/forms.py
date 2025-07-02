from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Trajet

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture', 'music_preference', 'animal_preference', 'smoking_preference']
        widgets = {
            'profile_picture': forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['phone_number'].required = False  # Optional based on your needs

class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        fields = ['depart', 'arrivee', 'date_depart', 'places_disponibles', 'prix_par_personne', 'description']
        widgets = {
            'date_depart': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CommunityJoinForm(forms.Form):
    community_id = forms.IntegerField()

class SearchTrajetForm(forms.Form):
    depart = forms.CharField(max_length=200, required=False)
    arrivee = forms.CharField(max_length=200, required=False)
    date_depart = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))