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
    path('media_stream/<int:id>/', views.stream_video, name='media_stream'),
    path('tags-suggest/', views.tags_suggest, name='tags_suggest'),
    path('get-items/<str:type>/', views.get_items, name='get_items'),
    path('delete-item/<str:type>/<int:id>/', views.delete_item, name='delete_item'),

    path("uploadElement/", views.uploadElement, name='uploadElement'),

    path("detailsAbout/<str:filtro>/<str:valor>/", views.detailsAbout, name='detailsAbout'),
    path('posts/', views.posts_recientes, name='posts_recientes'),
   # path('notificaciones/mencionar/', views.mencionar_usuario, name='mencionar_usuario'),
    path('notificaciones/count/', views.notificaciones_count, name='notificaciones_count'),
    path('notificaciones/obtener/', views.obtener_notificaciones, name='obtener_notificaciones'),

    path('adminPage/', views.adminPage, name='adminPage'),
    path("video/<str:id>/", views.watchContent, name='watchContent'),
    path('comic/<str:id>/', views.watchComic, name='watchComic'),
    path('edit/<str:tipo>/<int:pk>/', views.edit_objeto, name='edit_objeto'),
    path('crear-post/', views.crear_post, name='crear_post'),
    path('notificaciones/marcar_leida/', views.marcar_leida, name='marcar_leida'),
path('editar-post/<int:post_id>/', views.editar_post, name='editar_post'),

    path("navbarFilterHeader/", views.navbarFilterHeader, name='navbarFilterHeader'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('buscar/', views.multi_search_results, name='multi_search_results'),
    path('multi-search/', views.multi_search_results, name='multi_search_results'),
    path('descargar/', views.download_video, name='download_video'),
    #path('upload/comic/', views.upload_comic, name='upload_comic'),
    path('ajax_add_comment/<int:id>/', views.ajax_add_comment, name='ajax_add_comment'),
    path('deleteComic/<int:id>',views.deleteComic,name="deleteComic"),
    path('deleteVideo/<int:id>',views.deleteVideo,name="deleteVideo"),
    path('toggle-like/<str:model>/<int:pk>/', views.toggle_like, name='toggle_like'),
    path('comic/page/deleteComicImage/<int:id>', views.deleteComicImage, name='deleteComicImage'),
    path('descargas/', views.viewDownloadedVideos, name='viewDownloadedVideos'),
    path('descargas/eliminar/<str:filename>/', views.delete_file, name='delete_file'),
    path('profile/<str:username>',views.userProfile, name='userProfile'),
    path('profile/<str:username>/verLikes<str:filter>/',views.userProfileLikes, name='userProfileLikes'),
    path('pastNotifications/',views.pastNotifications, name='pastNotifications'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
