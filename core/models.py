from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    subscribed_publishers = models.ManyToManyField("Publisher", blank=True, related_name="subscribers")
    subscribed_journalists = models.ManyToManyField("CustomUser", blank=True, related_name="journalist_followers")
    newsletter_subscriptions = models.ManyToManyField("Newsletter", blank=True, related_name="subscribers")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    approved = models.BooleanField(default=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name="articles", null=True, blank=True)
    journalist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="articles", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("can_approve_article", "Can approve articles"),
            ("can_create_article", "Can create articles"),
        ]


class Newsletter(models.Model):
    TARGET_AUDIENCE_CHOICES = (
        ('all', 'All Users'),
        ('readers', 'Readers Only'),
        ('journalists', 'Journalists Only'),
        ('editors', 'Editors Only'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE_CHOICES, default='all')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_newsletters")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("can_create_newsletter", "Can create newsletters"),
            ("can_send_newsletter", "Can send newsletters"),
        ]
