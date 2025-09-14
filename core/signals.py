# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import requests
from .models import Article

@receiver(post_save, sender=Article)
def notify_article_published(sender, instance, created, **kwargs):
    if instance.approved:
        subscribers = []
        if instance.publisher:
            subscribers += instance.publisher.subscribers.all()
        if instance.journalist:
            subscribers += instance.journalist.journalist_followers.all()
        emails = [user.email for user in subscribers if user.email]
        if emails:
            send_mail(
                f"New Article: {instance.title}",
                instance.content,
                'admin@newsapp.com',
                emails
            )

        requests.post(
            "https://api.x.com/...",
            data={"status": f"New Article Published: {instance.title}"}
        )
