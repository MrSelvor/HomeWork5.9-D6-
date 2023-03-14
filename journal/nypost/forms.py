from django import forms
from .models import Post, Author
from django.core.exceptions import ValidationError
from datetime import datetime

class PostForm(forms.ModelForm):
    heading = forms.CharField(min_length=20)
    author = Author.objects.all().values('auth__user').values('auth')

    class Meta:
        model = Post
        fields = [
            'heading',
            'author',
            'text',
        ]

    def clean(self):
        cleaned_data = super().clean()
        heading = cleaned_data.get("heading")
        text = cleaned_data.get("text")
        if heading == text:
            raise ValidationError("Описание не должно быть идентично названию.")
        return cleaned_data