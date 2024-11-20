from django import forms
from django.core.validators import FileExtensionValidator
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
    # TODO: file size validation
    file = forms.FileField(validators=[FileExtensionValidator(['csv'], 'Only .csv files are allowed')])
    option = forms.ChoiceField(
        choices=[
            ('new-lists', 'Create all new Lists'),
            ('existing-lists', 'Includes existing Lists'),
            ('items-only', 'Import only Items'),
        ],
        help_text='''
            <ul>
                <li><b>Create all new Lists</b> - All Lists will be created as new, even if they already exist in this account.</li>
                <li><b>Includes existing Lists</b> - If a List with the same List ID already exists, the Items will be added to that existing List.</li>
                <li><b>Import only Items</b> - All Items will be added to an existing List with the same List ID. If no List exists, the Items will not be added.</li>
            </ul>
        ''',
        widget=forms.Select(attrs={'aria-describedby': 'id_option_helptext'}),
    )
