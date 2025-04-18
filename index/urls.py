from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
app_name = "index"

urlpatterns = [
    path("", views.index, name='index'),
    path('filtrar/<str:filter_type>/<str:string>/', views.filtered_media, name='filtered_media'),


    path("uploadElement/", views.uploadElement, name='uploadElement'),
    path("show/", views.show, name='show'),
    path("hide/", views.hide, name='hide'),
    path('adminPage/', views.adminPage, name='adminPage'),
    path("video/<int:id>/", views.watchContent, name='watchContent'),
    path("navbarFilterHeader/", views.navbarFilterHeader, name='navbarFilterHeader'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('buscar/', views.multi_search_results, name='multi_search_results'),
    path('multi-search/', views.multi_search_results, name='multi_search_results'),
    path('descargar/', views.download_video, name='download_video'),
    #path('upload_comic/', views.upload_comic, name='upload_comic'),
    path('upload/comic/', views.upload_comic, name='upload_comic'),
    path('comic/<int:id>/', views.watchComic, name='watchComic'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
