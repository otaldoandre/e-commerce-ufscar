from django import forms


class FinalizacaoPedidoForm(forms.Form):
    nome_cliente = forms.CharField(
        label='Nome completo',
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'name'}),
    )
    email_cliente = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    endereco_entrega = forms.CharField(
        label='Endereço de entrega',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'autocomplete': 'street-address',
        }),
    )
