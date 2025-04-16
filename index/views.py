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

from itertools import chain

def index(request):
    user = request.user

    # Verifica si se quiere mostrar todo
    show_all = request.GET.get('show_all') == 'true'

    if show_all:
        # Obtener TODO, sin importar si está oculto
        media_files = MediaFile.objects.all()
        comics = Comic.objects.all()
    else:
        # Solo mostrar los que no están ocultos
        media_files = MediaFile.objects.filter(hide=False)
        comics = Comic.objects.filter(hide=False)

    # Combinar y ordenar
    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )

    sidebar_context = get_sidebar_context()

    context = {
        'user': user,
        'media_files': combined_media,
        **sidebar_context
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

    if thing_to_filter == "Artistas":
        media_files = Artist.objects.all
    elif thing_to_filter == "Series":
        media_files = Game.objects.all
    elif thing_to_filter == "Personajes":
        media_files = Character.objects.all
    elif thing_to_filter == "Videos":
         media_files = MediaFile.objects.filter(isVideo=True).order_by('-uploaded_at')
    elif thing_to_filter == "Comics":
         media_files = Comic.objects.all
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
    terms = query.split()
    
    sidebar_context = get_sidebar_context()
    media_files_all = MediaFile.objects.filter(hide=False).order_by('-uploaded_at')

    media_results = MediaFile.objects.filter(hide=False)
    comic_results = Comic.objects.filter(hide=False)

    for term in terms:
        filters = (
            Q(name__icontains=term) |
            Q(artist__name__icontains=term) |
            Q(tags__name__icontains=term) |
            Q(game__name__icontains=term) |
            Q(character__name__icontains=term)
        )
        media_results = media_results.filter(filters)
        comic_results = comic_results.filter(filters)

    combined_results = sorted(
        chain(media_results.distinct(), comic_results.distinct()),
        key=lambda x: x.uploaded_at,
        reverse=True
    )

    context = {
        'results': combined_results,
        'search_terms': terms,
        'media_files': media_files_all,  # si esto es solo para sidebar, puedes renombrarlo
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

def watchComic(request, id):
    comic = get_object_or_404(Comic, id=id)
    comentarios = Comentario.objects.filter(comicID = comic)
    form = addComentariosForm()
    comic_pages = ComicPage.objects.filter(comic=comic)
    sidebar_data = get_sidebar_context()
    if request.method == 'POST':
        # Si el formulario se ha enviado, procesar la subida del archivo
        form = addComentariosForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            
            # Asignar manualmente el usuario y el archivo mediaFile
            comentario.usuario = request.user  # Suponiendo que el usuario está autenticado
            comentario.comicID = comic  # Obtener el archivo subido

            # Guardar el objeto Comentario con los campos adicionales
            comentario.save()
            return redirect('index:watchComic', comic.id)  # Redirigir correctamente

    else:
        form = addComentariosForm()
    return render(request, 'index/watchComic.html', {
        'mediafile': comic,
        'comentarios': comentarios,
        'comic_pages':comic_pages,
        'form': form,
        **sidebar_data
    })

def watchContent(request, id):
    mediafile = get_object_or_404(MediaFile, id=id)

    if request.method == 'POST':
        # Si el formulario se ha enviado, procesar la subida del archivo
        form = addComentariosForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            
            # Asignar manualmente el usuario y el archivo mediaFile
            comentario.usuario = request.user  # Suponiendo que el usuario está autenticado
            comentario.mediaFileID = mediafile  # Obtener el archivo subido

            # Guardar el objeto Comentario con los campos adicionales
            comentario.save()
            return redirect('index:watchContent', mediafile.id)  # Redirigir correctamente

    else:
        form = addComentariosForm()
    
   
    mediafile = get_object_or_404(MediaFile, id=id)
    #pages = comicImages.objects.filter(mediaFile = mediafile)
    comentarios = Comentario.objects.filter(mediaFileID = mediafile)
    
   
    
    # Obtener el contexto de la sidebar
    sidebar_data = get_sidebar_context()

    return render(request, 'index/watchContent.html', {
        'mediafile': mediafile,
        #'pages':pages,
        'comentarios':comentarios,
        'form':form,
        **sidebar_data,  # Integrar datos de la sidebar en el contexto de la vista
    })


def filtered_media(request, filter_type, string):
    sidebar_context = get_sidebar_context()
    
 

    filter_map = {
        'tag': ('tags__name__icontains',),
        'artist': ('artist__name__icontains',),
        'character': ('character__name__icontains',),
        'game': ('game__name__icontains',)
    }

    filters = filter_map.get(filter_type)

    if not filters:
        return redirect('index:index')  # fallback por si el tipo es inválido

    media_query = {filters[0]: string, 'hide': False}
    media_files = MediaFile.objects.filter(**media_query).order_by('-uploaded_at')
    comics = Comic.objects.filter(**media_query).order_by('-uploaded_at')

    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )

    context = {
        'media_files': combined_media,
        **sidebar_context
    }
    return render(request, 'index/index.html', context)


import mimetypes

def uploadElement(request): 
    if request.method == 'POST':
        form = UploadElementForm(request.POST, request.FILES)
        if form.is_valid():
            media = form 

       
            media.save()  
            
            return HttpResponseRedirect('/')
        else:
            print("Errores del formulario:", form.errors)

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


def upload_comic(request):
    if request.method == 'POST':
        form = UploadComicForm(request.POST)
        images = request.FILES.getlist('images')  # nombre del input que sube las imágenes

        if form.is_valid():
            comic = form.save(commit=False)
            comic.image = images[0]
            comic.save()
            form.save_m2m()

            for idx, image in enumerate(images):
                ComicPage.objects.create(comic=comic, image=image, order=idx)

            return JsonResponse({'message': 'Comic subido con éxito'})
        else:
            return JsonResponse({'error': 'Formulario inválido', 'details': form.errors}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)





import os
import re
from django.shortcuts import render
from yt_dlp import YoutubeDL

def safe_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    return name.strip('_')



def download_video(request):
    context = {}

    if request.method == 'POST':
        url = request.POST.get('url')
        download_type = request.POST.get('download_type', 'video')

        if url:
            try:
                output_dir = 'media'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'  # Ajusta si usas Linux o macOS

                # Obtener información del video sin descargar
                with YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'video')
                    ext = 'mp3' if download_type == 'audio' else info.get('ext', 'mp4')
                    clean_title = safe_filename(title)
                    final_filename = f"{clean_title}_{download_type}.{ext}"
                    full_path = os.path.join(output_dir, final_filename)

                # Si ya existe el archivo, no lo descargamos de nuevo
                if os.path.exists(full_path):
                    context['title'] = title
                    context['filename'] = final_filename
                    context['already_downloaded'] = True
                    return render(request, 'index/download.html', context)

                # Configuración base
                ydl_opts = {
                    'ffmpeg_location': ffmpeg_path,
                    'noplaylist': True,
                    'quiet': True,
                    'nooverwrites': True,
                    'nopart': True,
                    'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
                }

                if download_type == 'audio':
                    ydl_opts.update({
                        'format': 'bestaudio',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                    })
                else:
                    ydl_opts.update({
                        'format': 'bestvideo+bestaudio/best',
                    })

                # Intentar descargar
                try:
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        downloaded_file = ydl.prepare_filename(info)

                        # Si es audio, cambiar nombre manualmente a .mp3
                        if download_type == 'audio':
                            downloaded_file = os.path.splitext(downloaded_file)[0] + '.mp3'

                        if os.path.exists(downloaded_file) and downloaded_file != full_path:
                            os.rename(downloaded_file, full_path)

                        context['title'] = title
                        context['filename'] = final_filename

                except Exception as e:
                    # Fallback sin ffmpeg o sin mezcla
                    fallback_opts = {
                        'format': 'bestaudio' if download_type == 'audio' else 'best',
                        'noplaylist': True,
                        'quiet': True,
                        'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
                        'nooverwrites': True,
                        'nopart': True,
                    }

                    with YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        downloaded_file = ydl.prepare_filename(info)

                        if download_type == 'audio':
                            downloaded_file = os.path.splitext(downloaded_file)[0] + '.mp3'

                        if os.path.exists(downloaded_file) and downloaded_file != full_path:
                            os.rename(downloaded_file, full_path)

                        context['title'] = title
                        context['filename'] = final_filename

            except Exception as e:
                context['error'] = f"⚠️ Error al descargar: {str(e)}"

    return render(request, 'index/download.html', context)
