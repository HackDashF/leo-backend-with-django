from django.urls import path
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/favicon.svg', permanent=True)

urlpatterns = [
    path('favicon.ico', favicon_view)
]
