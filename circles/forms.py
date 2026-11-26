from django import forms
from django.utils.text import slugify
from .models import Circle


class CircleCreateForm(forms.ModelForm):
    class Meta:
        model = Circle
        fields = ['name', 'description', 'topic_type', 'topic_value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nolan Fanclub'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'What is this circle about?',
            }),
            'topic_type': forms.Select(attrs={'class': 'form-select'}),
            'topic_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Christopher Nolan',
            }),
        }

    def save(self, commit=True):
        circle = super().save(commit=False)
        base = slugify(self.cleaned_data['name']) or 'circle'
        slug = base
        n = 1
        while Circle.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        circle.slug = slug
        if commit:
            circle.save()
        return circle
