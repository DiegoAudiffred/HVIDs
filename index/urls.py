from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
app_name = 'index'

urlpatterns = [
    path("", views.index, name='index'),
    path('filtrar/<str:filter_type>/<str:string>/', views.filtered_media, name='filtered_media'),
    path('media-stream/<int:id>/', views.stream_video, name='media_stream'),
    path('tags-suggest/', views.tags_suggest, name='tags_suggest'),
    path('get-items/<str:type>/', views.get_items, name='get_items'),
    path('delete-item/<str:type>/<int:id>/', views.delete_item, name='delete_item'),

    path("uploadElement/", views.uploadElement, name='uploadElement'),

    path("detailsAbout/<str:filtro>/<str:valor>/", views.detailsAbout, name='detailsAbout'),

    path('adminPage/', views.adminPage, name='adminPage'),
    path("video/<int:id>/", views.watchContent, name='watchContent'),
    path('comic/<int:id>/', views.watchComic, name='watchComic'),

    path("navbarFilterHeader/", views.navbarFilterHeader, name='navbarFilterHeader'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('buscar/', views.multi_search_results, name='multi_search_results'),
    path('multi-search/', views.multi_search_results, name='multi_search_results'),
    path('descargar/', views.download_video, name='download_video'),
    #path('upload/comic/', views.upload_comic, name='upload_comic'),
    path('ajax/comment/<int:id>/', views.ajax_add_comment, name='ajax_add_comment'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
