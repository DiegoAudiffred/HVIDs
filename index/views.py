from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from db.models import MediaFile, Tags
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages


def index(request):
    # Obtener todos los archivos multimedia
    media_files = MediaFile.objects.all()
    
    # Verificar los datos obtenidos
    for media_file in media_files:
        print(f"Title: {media_file.title}, Thumbnail: {media_file.thumbnail}, File: {media_file.file}")

    return render(request, 'index/index.html', {'media_files': media_files})

def watchContent(request, id):
    mediafile = get_object_or_404(MediaFile, id=id)

    # Extraer el ID del archivo de Google Drive si es un enlace de Google Drive
    drive_preview_url = None
    if mediafile.file and 'drive.google.com' in mediafile.file:
        try:
            file_id = mediafile.file.split('/d/')[1].split('/')[0]
            drive_preview_url = f"https://drive.google.com/file/d/{file_id}/preview"
        except IndexError:
            drive_preview_url = None

    return render(request, 'index/watchContent.html', {
        'mediafile': mediafile,
        'drive_preview_url': drive_preview_url
    })
