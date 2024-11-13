from django import forms
from django.forms import ModelForm, TextInput

from lists.models import Item


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'color', 'list']
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
            'list': TextInput(attrs={'type': 'hidden'})
        }


class EditItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'color']
        widgets = {
            'color': TextInput(attrs={'type': 'color'})
        }


class ImportForm(forms.Form):
    file = forms.FileField(required=False)
