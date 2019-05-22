from django.urls import path
from django.conf.urls import url, re_path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('login/', views.AuthView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('au_profile/', views.AuthorView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('search/', views.SearchView.as_view()),
    path('detail/', views.DetailView.as_view()),
    path('star/', views.StarView().as_view()),
    path('verify/',views.VerifyView().as_view()),
    # path('star_detail/', views.StarDetailView.as_view()),
    #path('follow/', views.FollowView.as_view()),
    path('buy/', views.BuyedView.as_view()),
    # path('resource_detail/', views.ResourceView().as_view()),
    url(r'avator/$', views.AvatorView.as_view()),
    # path('coworker/', views.CoworkerView.as_view()),
    # path('auction/', views.AuctionView.as_view()),
    path('recharge/', views.RechargeView.as_view()),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

]
