from django.urls import path
from . import views

app_name = "index"

urlpatterns = [
    path("", views.index, name='index'),
    path("filteredByTag/<str:string>", views.filteredByTag, name='filteredByTag'),
    path("filteredByArtist/<str:string>", views.filteredByArtist, name='filteredByArtist'),
    path("uploadElement/", views.uploadElement, name='uploadElement'),

    path("watchContent/<int:id>/", views.watchContent, name='watchContent'),
]
