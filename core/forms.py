from django import forms
from django.core.validators import RegexValidator

class TicketPurchaseForm(forms.Form):
    movie_title = forms.CharField(widget=forms.HiddenInput())
    adult_qty = forms.IntegerField(min_value=0, max_value=20, initial=0, label='Взрослый')
    student_qty = forms.IntegerField(min_value=0, max_value=20, initial=0, label='Студент')
    child_qty = forms.IntegerField(min_value=0, max_value=20, initial=0, label='Детский')

    def clean(self):
        cleaned_data = super().clean()
        quantities = [
            cleaned_data.get('adult_qty', 0),
            cleaned_data.get('student_qty', 0),
            cleaned_data.get('child_qty', 0),
        ]
        if sum(quantities) == 0:
            raise forms.ValidationError('Выберите хотя бы 1 билет.')
        return cleaned_data


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, label='Ваше имя')
    email = forms.EmailField(label='Ваш email')
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон (необязательно)',
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9\s\-\(\)]{7,20}$',
                message='Введите корректный номер телефона.',
            )
        ],
    )
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label='Сообщение')
