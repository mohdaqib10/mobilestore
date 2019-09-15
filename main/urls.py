from django.urls import path

from .views import UserSignUp, UserLogin, UserDetail,UserMobileList, UserMobileDetail, UserList


urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('signup/', UserSignUp.as_view(), name='sign-up'),
    path('login/', UserLogin.as_view(), name='login'),
    path('users/<int:uk>/mobiles/', UserMobileList.as_view(), name='user-mobile-list'),
    path('users/<int:uk>/mobiles/<int:pk>/', UserMobileDetail.as_view(), name='user-mobile-detail'),
]
