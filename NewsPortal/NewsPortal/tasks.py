from celery import shared_task
import time

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from news.models import Post


@shared_task
def notifications_after_post_created(pk):
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    title = post.title
    subscribers_users = []

    for cat in categories:
        subscribers = cat.subscribers.all()
        subscribers_users += [s for s in subscribers]

    for subscriber in subscribers_users:
        html_content = render_to_string(
            'flatpages/post_created_email.html',
            {
                'username': subscriber.username,
                'text': post.preview,
                'link': f'{settings.SITE_URL}/post/{pk}'
            }
        )

        msg = EmailMultiAlternatives(
            subject=title,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email],
        )

        msg.attach_alternative(html_content, 'text/html')
        msg.send()