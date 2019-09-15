from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q

from .models import UserMobile


@receiver(post_save, sender=UserMobile)
def toggle_person_primary_mobiles(sender, instance, *args, **kwargs):
    if instance.is_primary:
        UserMobile.objects.select_for_update(). \
            filter(~Q(id=instance.id), user=instance.user).update(is_primary=False)
