from django.db import models
from django.utils import timezone

from .utils import get_current_time, update_instance


class AbstractDatetime(models.Model):
    """
    Abstract date & time model
    """
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = get_current_time()
        super().save(*args, **kwargs)


class User(AbstractDatetime):
    """
    User profile model
    """
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    contact_list = models.TextField(
        null=True, blank=True, help_text="User's Mobile Contact List"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.__class__.__name__} - {self.name}'

    @property
    def primary_mobile(self):
        if self.mobiles.filter(is_primary=True).exists():
            return self.mobiles.filter(is_primary=True).latest('created_at')
        elif self.mobiles.filter().exists():
            return self.mobiles.filter().latest('created_at')
        else:
            return None

    @property
    def all_mobiles(self):
        return self.mobiles.all().order_by('-is_primary')


class UserToken(AbstractDatetime):
    """
    User token model
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='token', related_query_name='token'
    )
    token = models.CharField(max_length=100)
    expired_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "User Token"
        verbose_name_plural = "User Tokens"

    def __str__(self):
        return f'{self.__class__.__name__} - {self.token}'

    @staticmethod
    def is_authenticated(token):
        return UserToken.objects.filter(token=token, expired_at__gte=get_current_time().date()).exists()

    @staticmethod
    def update_user_token_expiry_date(instance):
        from .serializers import UserTokenSerializer
        update_data = UserTokenSerializer(instance).data
        update_data['expired_at'] = get_current_time().date()
        return update_instance(instance, UserTokenSerializer, data=update_data)


class UserMobile(AbstractDatetime):
    """
    Model to store user mobile data
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='mobiles', related_query_name='mobile',
    )
    mobile = models.CharField(max_length=15)
    is_spam = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Mobile"
        verbose_name_plural = "Mobiles"
        unique_together = ('user', 'mobile')

    def __str__(self):
        return f'{self.__class__.__name__} - {self.mobile}'
