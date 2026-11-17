from django.db import models


class Review(models.Model):
    author = models.CharField("Имя автора", max_length=120)
    text = models.TextField("Текст отзыва")
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.author}: {self.text[:30]}"
