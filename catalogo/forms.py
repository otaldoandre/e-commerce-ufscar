from django import forms

from .models import Categoria, Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'estoque', 'categoria', 'imagem', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'preco': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'estoque': forms.NumberInput(attrs={'min': '0'}),
            'imagem': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
