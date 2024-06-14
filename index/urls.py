from . import views
from django.urls import path

app_name = "index"

urlpatterns = [
    path("", views.index, name='index'),
    path("watchContent/<int:id>/", views.watchContent, name='watchContent'),
]