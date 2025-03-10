from django import forms
from.models import CustomList

class CustomListForm(forms.ModelForm):
    class Meta:
        model = CustomList
        fields= ['list_name', 'list_description']

