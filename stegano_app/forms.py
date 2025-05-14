# forms.py

from django import forms

class SteganalysisForm(forms.Form):
    image = forms.ImageField()

class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True)
    data_file = forms.FileField(required=False)
