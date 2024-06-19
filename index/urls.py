from django.urls import path
from . import views

app_name = "index"

urlpatterns = [
    path("", views.index, name='index'),
    
    path("watchContent/<int:id>/", views.watchContent, name='watchContent'),
]
