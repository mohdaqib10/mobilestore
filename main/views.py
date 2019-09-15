import uuid
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import User, UserToken, UserMobile
from .serializers import UserBasicSerializer, UserSerializer, UserMobileSerializer
from .utils import validate_mobile, get_delta_time, create_instance, update_instance, validate_required_field
from .custom_auth import UserAuthenticationAuthentication
from .pagination import DefaultPagination


class UserSignUp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        with atomic():
            validate_required_field(request, 'mobile')
            user_mobile = UserMobile.objects.filter(mobile=self.request.data['mobile'])
            if user_mobile.exists():
                raise ValidationError({'detail': 'This mobile number is already exists.'})

            validate_required_field(request, 'name')
            validate_mobile(self.request.data['mobile'])

            # Create User
            user = create_instance(UserBasicSerializer, data=self.request.data)

            # Create User token
            token = UserToken.objects.create(
                user=user, token=str(uuid.uuid4()), expired_at=get_delta_time(days=15).date())

            # Create User mobile
            mobile_data = {
                'user': user.id,
                'mobile': self.request.data['mobile'],
                'is_primary': self.request.data['is_primary'] if 'is_primary' in self.request.data else False
            }
            user_mobile = create_instance(UserMobileSerializer, data=mobile_data)
            data = UserBasicSerializer(user).data
            data['token'] = token.token
            data['expired_at'] = token.expired_at
            data['mobile'] = user_mobile.mobile
            return Response({'data': data}, status=status.HTTP_201_CREATED)


class UserLogin(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        validate_required_field(request, 'mobile')
        mobile = self.request.data['mobile']
        try:
            user_mobile = UserMobile.objects.filter(is_primary=True, mobile=mobile).latest('created_at')
            user_token = UserToken.objects.get(user=user_mobile.user)
            token = user_token.token
        except:
            raise ValidationError({'detail': 'mobile number is wrong. Please try with correct mobile number'})
        if UserToken.is_authenticated(token):
            UserToken.update_user_token_expiry_date(user_token)
            data = UserSerializer(user_mobile.user).data
            data['token'] = token
            data['expired_at'] = user_token.expired_at
            return Response({'data': data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError({'detail': 'Invalid mobile'})


class UserList(ListAPIView):
    model = User
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, BasicAuthentication, UserAuthenticationAuthentication)
    queryset = model.objects.all()

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('name', 'mobile__mobile')
    # ordering_fields = ('name', 'all_mobiles__is_primary', 'all_mobiles__is_spam', 'created_at')
    pagination_class = DefaultPagination


class UserDetail(RetrieveUpdateDestroyAPIView):
    model = User
    queryset = model.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, UserAuthenticationAuthentication, BasicAuthentication)

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        with atomic():
            if 'mobile' in request.data and request.data['mobile'] or 'is_primary' in self.request.data:
                validate_required_field(request, 'mobile_id')
                validate_required_field(request, 'mobile')
                validate_mobile(self.request.data['mobile'])
                user_mobile = get_object_or_404(UserMobile, id=self.request.data['mobile_id'])
                user_mobile.mobile = self.request.data['mobile']
                user_mobile.is_primary = self.request.data['is_primary'] if 'is_primary' in self.request.data else user_mobile.is_primary
                user_mobile.save()

            user = update_instance(user, UserBasicSerializer, data=self.request.data)
            return Response({'data': UserSerializer(user).data}, status=status.HTTP_200_OK)


class UserMobileList(ListCreateAPIView):
    model = UserMobile
    queryset = model.objects.all()
    serializer_class = UserMobileSerializer
    authentication_classes = (TokenAuthentication, UserAuthenticationAuthentication, BasicAuthentication)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['uk'])
        user_mobiles = user.mobiles.all()
        return user_mobiles

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        with atomic():
            user = get_object_or_404(User, id=self.kwargs['uk'])
            self.request.data['user'] = user.id
            validate_required_field(request, 'mobile')
            user_mobile = create_instance(self.serializer_class, data=self.request.data)
            return Response({'data': self.serializer_class(user_mobile).data}, status=status.HTTP_201_CREATED)


class UserMobileDetail(RetrieveUpdateDestroyAPIView):
    model = UserMobile
    queryset = model.objects.all()
    serializer_class = UserMobileSerializer
    authentication_classes = (TokenAuthentication, UserAuthenticationAuthentication, BasicAuthentication)

    def get_object(self):
        user = get_object_or_404(User, id=self.kwargs['uk'])
        try:
            user_mobile = user.mobiles.get(id=self.kwargs['pk'])
            return user_mobile
        except:
            raise Http404

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'is_spam' in self.request.data and self.request.data['is_spam']:
            self.request.data['count'] = instance.count + 1

        if 'mobile' in self.request.data and self.request.data['mobile']:
            validate_mobile(self.request.data['mobile'])
        spam_data = update_instance(instance, self.serializer_class, data=self.request.data)
        return self.partial_update(request, *args,**kwargs)
