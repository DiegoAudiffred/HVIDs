from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from db.models import MediaFile, Tags
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages

def index(request):
    # Obtener todos los archivos multimedia
    media_files = MediaFile.objects.all()
    print(media_files.count())  # Método count() debe ser llamado
    return render(request, 'index/index.html', {'media_files': media_files})

from django.shortcuts import get_object_or_404

def watchContent(request, id):
    # Obtener el archivo multimedia por ID
    media_file = get_object_or_404(MediaFile, id=id)
    print(media_file.id)  # Imprimir el ID para verificar la obtención correcta
    return render(request, 'index/watchContent.html', {'mediafile': media_file})
