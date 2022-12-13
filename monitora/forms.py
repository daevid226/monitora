from django import forms

class FilterForm(forms.Form):
    search_text = forms.CharField(label='Enter search text', max_length=100)

 