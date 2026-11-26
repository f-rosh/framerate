from django import forms
from .models import Review, Comment


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} \u2605') for i in range(1, 6)],
        widget=forms.RadioSelect,
        initial='1',
    )

    class Meta:
        model = Review
        fields = ['rating', 'circle', 'body']
        widgets = {
            'circle': forms.Select(attrs={'class': 'form-select'}),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write your review...',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only let the user tag a review to a circle they've joined.
        # When editing, keep the already-tagged circle selectable even if
        # they later left it.
        from circles.models import Circle
        if user and user.is_authenticated:
            qs = Circle.objects.filter(memberships__user=user).distinct()
            if self.instance and self.instance.pk and self.instance.circle_id:
                qs = qs | Circle.objects.filter(pk=self.instance.circle_id)
            self.fields['circle'].queryset = qs.distinct()
        else:
            self.fields['circle'].queryset = Circle.objects.none()
        self.fields['circle'].required = False
        self.fields['circle'].empty_label = 'No circle (general review)'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...',
            }),
        }
