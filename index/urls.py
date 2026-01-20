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
    path("watchVideo/<int:id>/", views.watchVideo, name='watchVideo'),
    path('watchComic/<int:id>/', views.watchComic, name='watchComic'),
    path('recentPosts/', views.recentPosts, name='recentPosts'),
    path('createPost/', views.createPost, name='createPost'),
    path('uploadFile/', views.uploadFile, name='uploadFile'),
    path('videoDownloader/', views.videoDownloader, name='videoDownloader'),
    path('userProfile/<str:username>',views.userProfile, name='userProfile'),
    path("navbarFilterHeader/", views.navbarFilterHeader, name='navbarFilterHeader'),

    path('downloadedVideos/', views.viewDownloadedVideos, name='viewDownloadedVideos'),
    path('downloadedVideos/delete/<str:filename>/', views.deleteDownloadedVideo, name='deleteDownloadedVideo'),
    path('downloadedVideos/upload/<str:filename>/', views.uploadDownloadedVideo, name='uploadDownloadedVideo'),

    path('adminPage/', views.adminPage, name='adminPage'),
    path('get_characters_by_game/', views.get_characters_by_game, name='get_characters_by_game'),


    path('filtrar/<str:filter_type>/<str:string>/', views.filtered_media, name='filtered_media'),
    path('media_stream/<int:id>/', views.stream_video, name='media_stream'),
    path('tags-suggest/', views.tags_suggest, name='tags_suggest'),
    path('get-items/<str:type>/', views.get_items, name='get_items'),
path('load-audio/<int:media_id>/', views.load_audio, name='load_audio'),

    path("uploadFile/", views.uploadFile, name='uploadFile'),

    path("detailsAbout/<str:filtro>/<str:valor>/", views.detailsAbout, name='detailsAbout'),
   # path('notificaciones/mencionar/', views.mencionar_usuario, name='mencionar_usuario'),
    path('notificaciones/count/', views.notificaciones_count, name='notificaciones_count'),
    path('notificaciones/obtener/', views.obtener_notificaciones, name='obtener_notificaciones'),


    path('edit/<str:tipo>/<int:pk>/', views.edit_objeto, name='edit_objeto'),
    path('eliminar_post/<int:id>', views.eliminar_post,name='eliminar_post'),

    path('notificaciones/marcar_leida/', views.marcar_leida, name='marcar_leida'),
path('editar-post/<int:post_id>/', views.editar_post, name='editar_post'),
        path("allVideosHide/", views.allVideosHide, name='allVideosHide'),

    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('buscar/', views.multi_search_results, name='multi_search_results'),
    path('multi-search/', views.multi_search_results, name='multi_search_results'),
    path('ajax_add_comment/<int:id>/', views.ajax_add_comment, name='ajax_add_comment'),
    path('deleteComic/<int:id>',views.deleteComic,name="deleteComic"),
    path('deleteVideo/<int:id>',views.deleteVideo,name="deleteVideo"),
    path('toggle-like/<str:model>/<int:pk>/', views.toggle_like, name='toggle_like'),
    path('comic/page/deleteComicImage/<int:id>', views.deleteComicImage, name='deleteComicImage'),


    
    path('profile/<str:username>/verLikes<str:filter>/',views.userProfileLikes, name='userProfileLikes'),
    path('pastNotifications/',views.pastNotifications, name='pastNotifications'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
