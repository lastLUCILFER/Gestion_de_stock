from django import forms
from .models import Client, Produit, Commande, DetailCommande
from django.core.validators import MinLengthValidator
import hashlib

class ClientForm(forms.ModelForm):
    nom = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(max_length=200, required=True)
    adresse = forms.CharField(max_length=300, required=False)
    telephone = forms.CharField(max_length=50, required=False)
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(),
        validators=[MinLengthValidator(6)]
    )
    confirm_password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput()
    )

    class Meta: 
        model = Client
        fields = ['nom', 'email', 'adresse', 'telephone', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return confirm_password

    def save(self, commit=True):
        client = super().save(commit=False)
        # Hash the password before saving
        password = self.cleaned_data['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        client.password = hashed_password
        if commit:
            client.save()
        return client

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=200, required=True)
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Hash the password to compare with stored hash
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                client = Client.objects.get(email=email, password=hashed_password)
                cleaned_data['client'] = client
            except Client.DoesNotExist:
                raise forms.ValidationError('Invalid email or password.')
        return cleaned_data

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['statut']
        widgets = {
            'statut': forms.Select(choices=[
                ('En attente', 'En attente'),
                ('En cours', 'En cours'),
                ('Livré', 'Livré'),
                ('Annulé', 'Annulé')
            ])
        }

class DetailCommandeForm(forms.ModelForm):
    class Meta:
        model = DetailCommande
        fields = ['produit', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': 1})
        }
