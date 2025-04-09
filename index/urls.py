from django.urls import path
from . import views

app_name = "index"

urlpatterns = [
    path("", views.index, name='index'),
    path("filteredByTag/<str:string>", views.filteredByTag, name='filteredByTag'),
    path("filteredByArtist/<str:string>", views.filteredByArtist, name='filteredByArtist'),
    path("filteredByCharacter/<str:string>", views.filteredByCharacter, name='filteredByCharacter'),
    path("filteredByGame/<str:string>", views.filteredByGame, name='filteredByGame'),

    path("uploadElement/", views.uploadElement, name='uploadElement'),
    path("show/", views.show, name='show'),
    path("hide/", views.hide, name='hide'),
    path('adminPage/', views.adminPage, name='adminPage'),
    path("watchContent/<int:id>/", views.watchContent, name='watchContent'),

]
