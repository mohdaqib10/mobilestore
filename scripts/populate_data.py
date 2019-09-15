import uuid
import random
import string

from main.serializers import UserBasicSerializer, UserTokenSerializer, UserMobileSerializer
from main.models import User
from main.utils import get_delta_time, create_instance

from faker import Faker
fake = Faker()


def random_mobile_generator():
    return ''.join(random.choice(string.digits) for i in range(10))


def create_users_with_token(num):
    for i in range(num):
        data = {
            'name': fake.name(),
            'email': fake.email()
        }
        user = create_instance(UserBasicSerializer, data=data)
        data = {
            'user': user.id,
            'token': str(uuid.uuid4()),
            'expired_at': get_delta_time(days=15).date()
        }
        create_instance(UserTokenSerializer, data=data)


def create_user_mobiles():
    for user in User.objects.all():
        for i in range(random.randrange(4, 10)):
            data = {
                'user': user.id,
                'mobile': random_mobile_generator(),
                'is_primary': random.choice([True, False])
            }
            create_instance(UserMobileSerializer, data=data)


def run():
    create_users_with_token(50)
    create_user_mobiles()
