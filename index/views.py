import random
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from db.models import *
from .forms import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.shortcuts import render
from pytube import YouTube
import os
from django.conf import settings
# views.py

import mimetypes
def get_sidebar_context():
    popular_tags = Tags.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]

    popular_artists = Artist.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]

    popular_characters = Character.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]
    
    popular_games = Game.objects.annotate(num_mediafiles=Count('mediafile')).order_by('-num_mediafiles')[:10]


    #random_Tags = list(Tags.objects.all())
    #random_items = random.sample(random_Tags, 3)
    #random_item = random.choice(items)

    return {
        'popular_tags': popular_tags,
        'popular_artists': popular_artists,
        'popular_characters':popular_characters,
        'popular_games':popular_games,

        #'random_items':random_items
        }

def index(request):
    user= request.user
    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
    sidebar_context = get_sidebar_context()

    context = {
        'user':user,
        'media_files': media_files,
        **sidebar_context  # Unir el contexto de la sidebar
    }

    return render(request, 'index/index.html', context)

def show(request):
    media_files = MediaFile.objects.all()
    for med in media_files:
        med.hide = False
        med.save()  # Guardar cada instancia actualizada
    
    return redirect('index:index')  # Redirigir correctamente

from django.shortcuts import redirect

def adminPage(request):
    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at')
    sidebar_context = get_sidebar_context()

    formTag = addTagsForm()
    formArtist = addArtistForm()
    formUser = addUserForm()
    formChar = addCharsForm()
    formGame = addGameForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'tag_form':
            formTag = addTagsForm(request.POST, request.FILES)
            if formTag.is_valid():
                formTag.save()
                return redirect('index:adminPage')

        elif form_type == 'artist_form':
            formArtist = addArtistForm(request.POST, request.FILES)
            if formArtist.is_valid():
                formArtist.save()
                return redirect('index:adminPage')

        elif form_type == 'user_form':
            formUser = addUserForm(request.POST, request.FILES)
            if formUser.is_valid():
                formUser.save()
                return redirect('index:adminPage')
        elif form_type == 'game_form':
            formGame = addGameForm(request.POST, request.FILES)
            if formGame.is_valid():
                formGame.save()
                return redirect('index:adminPage')
        elif form_type == 'char_form':
            formChar = addCharsForm(request.POST, request.FILES)
            if formChar.is_valid():
                formChar.save()
                return redirect('index:adminPage')

    context = {
        'formTag': formTag,
        'formArtist': formArtist,
        'formUser': formUser,
        'formChar': formChar,
        'formGame':formGame,
        'media_files': media_files,
        **sidebar_context
    }

    return render(request, 'index/adminPage.html', context)
    
def navbarFilterHeader(request):
    thing_to_filter = request.GET.get('filter')

    if thing_to_filter == "artistas":
        media_files = Artist.objects.all
    elif thing_to_filter == "series":
        media_files = Game.objects.all
    elif thing_to_filter == "personajes":
        media_files = Character.objects.all
    elif thing_to_filter == "videos":
         media_files = MediaFile.objects.filter(isVideo=True).order_by('-uploaded_at')
    elif thing_to_filter == "comics":
         media_files = MediaFile.objects.filter(isVideo=False).order_by('-uploaded_at')
    else:
        media_files = MediaFile.objects.filter().order_by('-uploaded_at')

    sidebar_context = get_sidebar_context()

    context = {
        'media_files': media_files,
        'filter_selected': thing_to_filter,
        **sidebar_context
    }
    return render(request, 'index/navbarFilterHeader.html', context)

def autocomplete(request):
    term = request.GET.get('term', '')
    results = set()

    if term:
        tags = Tags.objects.filter(name__istartswith=term).values_list('name', flat=True)
        artists = Artist.objects.filter(name__istartswith=term).values_list('name', flat=True)
        games = Game.objects.filter(name__istartswith=term).values_list('name', flat=True)
        characters = Character.objects.filter(name__istartswith=term).values_list('name', flat=True)

        results.update(tags)
        results.update(artists)
        results.update(games)
        results.update(characters)

    return JsonResponse(list(results), safe=False)

#def multi_search_results(request):
#    query = request.GET.get('q', '')
#    terms = query.strip().split()
#
#    tags = Tags.objects.none()
#    artists = Artist.objects.none()
#    games = Game.objects.none()
#    characters = Character.objects.none()
#    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
#    sidebar_context = get_sidebar_context()
#
#
#    for term in terms:
#        tags |= Tags.objects.filter(name__icontains=term)
#        artists |= Artist.objects.filter(name__icontains=term)
#        games |= Game.objects.filter(name__icontains=term)
#        characters |= Character.objects.filter(name__icontains=term)
#
#    context = {
#        'query': query,
#        'tags': tags.distinct(),
#        'artists': artists.distinct(),
#        'games': games.distinct(),
#        'characters': characters.distinct(),
#        'media_files': media_files,
#        **sidebar_context  # Unir el contexto de la sidebar
#    }
#    return render(request, 'index/multi_search_results.html', context)

def multi_search_results(request):
    query = request.GET.get("q", "").strip()
    terms = query.split()  # Divide por espacios
    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
    sidebar_context = get_sidebar_context()
    results = MediaFile.objects.all()

    for term in terms:
        results = results.filter(
            Q(name__icontains=term) |
            Q(artist__name__icontains=term) |
            Q(tags__name__icontains=term) |
            Q(game__name__icontains=term) |
            Q(character__name__icontains=term)
        )

    results = results.distinct().order_by('-uploaded_at')

    context = {
        'results': results,
        'search_terms': terms,
        'media_files': media_files,
        **sidebar_context  
    }
    return render(request, 'index/multi_search_results.html', context)


def hide(request):
    futa_tag = Tags.objects.get(name='Futa')  # Obtener el objeto Tag con el nombre 'futa'
    media_files = MediaFile.objects.filter(tags=futa_tag)    
    for med in media_files:
        med.hide = True
        med.save()  # Guardar cada instancia actualizada
    
    return redirect('index:index')  # Redirigir correctamente

def watchContent(request, id):
    mediafile = get_object_or_404(MediaFile, id=id)

    if request.method == 'POST':
        # Si el formulario se ha enviado, procesar la subida del archivo
        form = addComentariosForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            
            # Asignar manualmente el usuario y el archivo mediaFile
            comentario.usuario = request.user  # Suponiendo que el usuario está autenticado
            comentario.mediaFile = mediafile  # Obtener el archivo subido

            # Guardar el objeto Comentario con los campos adicionales
            comentario.save()
            return redirect('index:watchContent', mediafile.id)  # Redirigir correctamente

    else:
        form = addComentariosForm()
    
   
    mediafile = get_object_or_404(MediaFile, id=id)
    #pages = comicImages.objects.filter(mediaFile = mediafile)
    comentarios = Comentario.objects.filter(mediaFile = mediafile)
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
        #'pages':pages,
        'comentarios':comentarios,
        'form':form,
        **sidebar_data,  # Integrar datos de la sidebar en el contexto de la vista
    })


def filteredByTag(request, string):
    # Filtrar MediaFiles por el nombre del tag
    if string == 'All':
        media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
        sidebar_context = get_sidebar_context()
        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }   

        return redirect('index:index')

    else: 
        media_files = MediaFile.objects.filter(tags__name__icontains=string,hide=False).order_by('-uploaded_at')
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
        media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
        sidebar_context = get_sidebar_context()
        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }   

        return redirect('index:index')    
    else: 
        media_files = MediaFile.objects.filter(artist__name__icontains=string, hide=False).order_by('-uploaded_at')
    # Obtener el contexto de la sidebar
        sidebar_context = get_sidebar_context()

        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }
        return render(request, 'index/index.html', context)


def filteredByCharacter(request, string):

    if string == 'All':
        media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
        sidebar_context = get_sidebar_context()
        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }   

        return redirect('index:index')
    else: 
        media_files = MediaFile.objects.filter(character__name__icontains=string, hide=False).order_by('-uploaded_at')
    # Obtener el contexto de la sidebar
        sidebar_context = get_sidebar_context()
        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }
        return render(request, 'index/index.html', context)

def filteredByGame(request, string):

    # Filtrar MediaFiles por el nombre del tag
    if string == 'All':
        media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
        sidebar_context = get_sidebar_context()
        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }   

        return redirect('index:index')
    else: 
        media_files = MediaFile.objects.filter(game__name__icontains=string, hide=False).order_by('-uploaded_at')
    # Obtener el contexto de la sidebar
        sidebar_context = get_sidebar_context()

        context = {
            'media_files': media_files,
            **sidebar_context  # Unir el contexto de la sidebar
        }
        return render(request, 'index/index.html', context)

import mimetypes

def uploadElement(request): 
    if request.method == 'POST':
        form = UploadElementForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)  

            uploaded_file = request.FILES.get('file')  
            if uploaded_file:
                mime_type, _ = mimetypes.guess_type(uploaded_file.name)
                if mime_type and mime_type.startswith('video'):
                    media.isVideo = True
                else:
                    media.isVideo = False
                media.user=request.user
            media.save()  
            form.save_m2m()  

            return HttpResponseRedirect('/')
    else:
        form = UploadElementForm()
        formComic=UploadComicForm()
    
    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at').all()
    sidebar_context = get_sidebar_context()

    context = {
        'form': form,
        'formComic':formComic,
        'media_files': media_files,
        **sidebar_context
    }

    return render(request, 'index/uploadElement.html', context)






from django.shortcuts import render
import yt_dlp
import imageio_ffmpeg
import os

from django.shortcuts import render
import yt_dlp
import imageio_ffmpeg
import os

def download_video(request):
    context = {}

    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            try:
                # Obtener la ruta al ejecutable de ffmpeg instalado vía imageio
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'ffmpeg_location': ffmpeg_path,
                    'merge_output_format': 'mp4',
                    'outtmpl': 'media/%(title).100s.%(ext)s',
                    'postprocessors': [
                        {'key': 'FFmpegMerger'}  # ← sin argumentos adicionales
                    ],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    final_filename = os.path.splitext(filename)[0] + '.mp4'

                    context['title'] = info.get('title', 'Video descargado')
                    context['filename'] = final_filename

            except Exception as e:
                context['error'] = f"⚠️ Ocurrió un error al descargar el video: {str(e)}"

    return render(request, 'index/download.html', context)






