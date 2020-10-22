from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.Djangosaml2SignupView.as_view(),
         name='saml2_signup'),
]
