from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ["author", "text"]
        widgets = {
            "author": forms.TextInput(attrs={"placeholder": "Ваше имя"}),
            "text": forms.Textarea(attrs={"placeholder": "Ваш отзыв", "rows": 4}),
        }

    def clean_author(self):
        author = self.cleaned_data.get("author", "")
        if author is not None:
            author = author.strip()
        if not author:
            raise forms.ValidationError("Имя не может быть пустым.")
        return author

    def clean_text(self):
        text = self.cleaned_data.get("text", "")
        if text is not None:
            text = text.strip()
        if not text:
            raise forms.ValidationError("Текст не может быть пустым.")
        return text
