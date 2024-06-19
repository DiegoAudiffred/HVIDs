from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.db.models import Count
from db.models import *
import random

def get_sidebar_context():
    popular_tags = Tags.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]

    popular_artists = Artist.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]

    popular_characters = Character.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]
    
    

    random_Tags = list(Tags.objects.all())

    random_items = random.sample(random_Tags, 3)
    #random_item = random.choice(items)

    return {
        'popular_tags': popular_tags,
        'popular_artists': popular_artists,
        'popular_characters':popular_characters,
        'random_items':random_items
        }

def index(request):
    media_files = MediaFile.objects.order_by('-uploaded_at').all()
    sidebar_context = get_sidebar_context()

    context = {
        'media_files': media_files,
        **sidebar_context  # Unir el contexto de la sidebar
    }

    return render(request, 'index/index.html', context)


def watchContent(request, id):
    try:
        # Decodificar el hash para obtener el ID original
        id = hashids.decode(id)[0]
    except IndexError:
        raise Http404("No such content")

    mediafile = get_object_or_404(MediaFile, id=id)
    drive_preview_url = None
    
    # Lógica para obtener el enlace de vista previa de Google Drive si es necesario
    if mediafile.file and 'drive.google.com' in mediafile.file:
        try:
            file_id = mediafile.file.split('/d/')[1].split('/')[0]
            drive_preview_url = f"https://drive.google.com/file/d/{file_id}/preview"
        except IndexError:
            drive_preview_url = None
    
    # Obtener el contexto de la sidebar
    sidebar_data = get_sidebar_context()

    return render(request, 'index/watchContent.html', {
        'mediafile': mediafile,
        'drive_preview_url': drive_preview_url,
        **sidebar_data,  # Integrar datos de la sidebar en el contexto de la vista
    })


def filteredByTag(request, string):
    # Filtrar MediaFiles por el nombre del tag
    if string == 'All':
        media_files = MediaFile.objects.order_by('-uploaded_at').all()
    else: 
        media_files = MediaFile.objects.filter(tags__name__icontains=string).order_by('-uploaded_at')
    # Obtener el contexto de la sidebar
    sidebar_context = get_sidebar_context()

    context = {
        'media_files': media_files,
        **sidebar_context  # Unir el contexto de la sidebar
    }
    return render(request, 'index/index.html', context)


def filteredByArtist(request, string):
    # Filtrar MediaFiles por el nombre del tag
    if string == 'All':
        media_files = MediaFile.objects.order_by('-uploaded_at').all()
    else: 
        media_files = MediaFile.objects.filter(artist__name__icontains=string).order_by('-uploaded_at')
    # Obtener el contexto de la sidebar
    sidebar_context = get_sidebar_context()

    context = {
        'media_files': media_files,
        **sidebar_context  # Unir el contexto de la sidebar
    }
    return render(request, 'index/index.html', context)