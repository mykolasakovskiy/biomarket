from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="ПІБ", max_length=120)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Телефон", max_length=32)
    address = forms.CharField(label="Адреса", max_length=255)
    city = forms.CharField(label="Місто", max_length=120)
    postal_code = forms.CharField(label="Поштовий індекс", max_length=20)
    notes = forms.CharField(label="Коментар", widget=forms.Textarea, required=False)
