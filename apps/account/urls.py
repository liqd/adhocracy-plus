from django.urls import path

from . import views

urlpatterns = [
    path(
        "", views.AccountView.as_view(), name="account"
    ),  # https://aplus.csariel.xyz/account/
    path(
        "profile/", views.ProfileUpdateView.as_view(), name="account_profile"
    ),  # https://aplus.csariel.xyz/account/profile/
    path(
        "account_deletion/",
        views.AccountDeletionView.as_view(),
        name="account_deletion",
    ),
    path(
        "agreements/",  # https://aplus.csariel.xyz/account/agreements/
        views.OrganisationTermsOfUseUpdateView.as_view(),
        name="user_agreements",
    ),
]
