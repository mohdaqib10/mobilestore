# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from .models import UserToken


class UserAuthenticationAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            try:
                if UserToken().is_authenticated(token):
                    return None
                else:
                    raise AuthenticationFailed({'detail': 'You are not authorised to perform this action'})
            except Exception as e:
                raise AuthenticationFailed({'detail': 'You are not authorised to perform this action'})
        else:
            raise AuthenticationFailed({'detail': 'You are not authorised to perform this action'})
