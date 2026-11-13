from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        min_length=8,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    confirmacao_senha = forms.CharField(
        label='Confirme a senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'telefone': forms.TextInput(attrs={'autocomplete': 'tel'}),
            'endereco': forms.Textarea(
                attrs={'rows': 4, 'autocomplete': 'street-address'}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Cliente.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe um cliente com este e-mail.')
        from django.contrib.auth import get_user_model
        if get_user_model().objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('Já existe um usuário com este e-mail.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get('senha')
            and cleaned_data.get('confirmacao_senha')
            and cleaned_data['senha'] != cleaned_data['confirmacao_senha']
        ):
            self.add_error('confirmacao_senha', 'As senhas não conferem.')
        return cleaned_data


class LoginClienteForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    senha = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

