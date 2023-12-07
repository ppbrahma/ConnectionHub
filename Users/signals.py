from typing import Type

from django.core.mail import EmailMessage
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from Notifications.models import Notification
from Users.models import User, Follow

PASSWORD_CHANGED_MESSAGE = ''''''

WELCOME_MESSAGE = ''' '''


@receiver(post_save, sender=User)
def welcome_notification(sender: Type[User], instance: User, created: bool, **kwargs):
    if created:
        Notification.create_notification(
            recipient=instance,
            notification_type='welcome',
            content='Welcome to our community!'
        )
        subject = 'Welcome to ConnectionHub'
        html_message = render_to_string(
            'email-template.html',
            {
                'name': instance.full_name,
                'message': WELCOME_MESSAGE
            }
        )
        message = EmailMessage(
            subject=subject,
            body=html_message,
            to=[instance.email],
        )
        message.content_subtype = 'html'
        message.send(fail_silently=True)


@receiver(post_save, sender=Follow)
def follow_signal(sender: Type[Follow], instance: Follow, created: bool, **kwargs):
    if created:
        instance.followee.followers_count += 1
        instance.followee.save()
        instance.follower.followings_count += 1
        instance.follower.save()

        Notification.create_notification(
            recipient=instance.followee,
            notification_type='follow',
            content=f'{instance.follower} started following you',
            arg_value=str(instance.follower.username)
        )


@receiver(post_delete, sender=Follow)
def unfollow_signal(sender: Type[Follow], instance: Follow, **kwargs):
    instance.followee.followers_count -= 1
    instance.follower.followings_count -= 1
    instance.followee.save()
    instance.follower.save()


@receiver(pre_save, sender=User)
def user_updated(sender, **kwargs):
    user: User = kwargs.get('instance', None)
    if not user:
        return
    if not User.objects.filter(pk=user.pk).exists():
        return

    new_password = user.password
    new_username = user.username

    try:
        old_password = User.objects.get(pk=user.pk).password
        old_username = User.objects.get(pk=user.pk).username
    except User.DoesNotExist:
        old_password = None
        old_username = None

    if new_password != old_password:
        subject = 'Your password is changed'
        html_message = render_to_string(
            'email-template.html',
            {
                'name': user.full_name,
                'message': PASSWORD_CHANGED_MESSAGE
            }
        )
        message = EmailMessage(
            subject=subject,
            body=html_message,
            to=[user.email],
        )
        message.content_subtype = 'html'
        message.send(fail_silently=True)

    if new_username != old_username:
        subject = 'Your username is changed'
        html_message = render_to_string(
            'email-template.html',
            {
                'name': user.full_name,
                'message': USERNAME_CHANGED_MESSAGE.format(username=new_username)
            }
        )
        message = EmailMessage(
            subject=subject,
            body=html_message,
            to=[user.email],
        )
        message.content_subtype = 'html'
        message.send(fail_silently=True)
