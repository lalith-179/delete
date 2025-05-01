from django import forms
from .models import *


# create a ModelForm
class filmForm(forms.ModelForm):

    class Meta:
        model = film
        fields = ('movie_name', 'movie_lang', 'movie_year', 'url')

    def __str__(self):
        return self.movie_name


class showForm(forms.ModelForm):

    class Meta:
        model = show
        fields = ('movie', 'start_date', 'end_date','showtime', 'price')
        labels = {
            'movie':'Select a Movie',
            'start_date':'Show Start Date',
            'end_date':'Show End Date',
            'showtime': 'Show time',
            'price': 'Ticket Price'
        }
        widgets = {
            'movie': forms.Select(attrs={
                'class': 'form-control select2',
                'placeholder': 'Select a movie for the show'
            }),
            # Using standard DateInput with type='date' which expects YYYY-MM-DD format
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control date-input'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control date-input'
            }),
            'showtime': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control',
                'placeholder': 'HH:MM'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ticket price',
                'min': '0',
                'step': '0.01'
            })
        }
        
        help_texts = {
            'start_date': 'Use the date picker or enter date in YYYY-MM-DD format',
            'end_date': 'Use the date picker or enter date in YYYY-MM-DD format',
        }
    def __str__(self):
        return self.movie_name