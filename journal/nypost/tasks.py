from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category
import datetime



def send_notifications(preview, pk, heading, subscribers):
    html_content = render_to_string(
        'post_created_emails.html',
        {
           'text':preview,
            'link':f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=heading,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@shared_task
def notify_about_new_post(pk):
    post = Post.objects.get(pk=pk)
    category_post = post.category_post.all()
    subscribers_emails = []

    for cat in category_post:
        subscribers = cat.subscribers.all()
        subscribers_emails += [s.email for s in subscribers]

    send_notifications(post.preview(), post.pk, post.heading, subscribers_emails)

@shared_task
def notify_every_week():
   last_week = datetime.datetime.now() - datetime.timedelta(days=7)
   posts = Post.objects.filter(date_create__gte=last_week)
   category_post = set(posts.values_list('categories__cat_name', flat=True))
   subscribers = set(Category.objects.filter(cat__in=category_post).values_list('subscribers__email', flat=True))

   html_content = render_to_string(
       'weekly_post.html',
       {
           'link': settings.SITE_URL,
           'posts': posts,
       }
   )

   msg = EmailMultiAlternatives(
       subject='Статьи за неделю',
       body='',
       from_email=settings.DEFAULT_FROM_EMAIL,
       to=subscribers,
   )

   msg.attach_alternative(html_content, 'text/html')
   msg.send()