from django.db import models

class Moment(models.Model):
    CATEGORY_CHOICES = [
        ('important', '⭐ Важлива подія'),
        ('default', '🎈 Затишний момент'),
        ('funny', '😹 Смішно'),
        ('romantic', 'романтично'),



    ]

    PERIOD_CHOICES = [
        ('0-3', '0–3 місяці'),
        ('3-6', '3–6 місяців'),
        ('6-9', '6–9 місяців'),
        ('9-12', '9–12 місяців'),
        ('1plus', '1+ рік'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='0-3')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='default')
    location = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to='moments_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MomentPhoto(models.Model):
    moment = models.ForeignKey(
        Moment,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(upload_to='moments_photos/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Фото для {self.moment.title}'


class BucketItem(models.Model):
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
