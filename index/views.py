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

    # Obtener ambos tipos de archivos visibles
    media_files = MediaFile.objects.filter(hide=False)
    comics = Comic.objects.filter(hide=False)

    # Combinar y ordenar todos por fecha de subida
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

    if thing_to_filter == "artistas":
        media_files = Artist.objects.all
    elif thing_to_filter == "series":
        media_files = Game.objects.all
    elif thing_to_filter == "personajes":
        media_files = Character.objects.all
    elif thing_to_filter == "videos":
         media_files = MediaFile.objects.filter(isVideo=True).order_by('-uploaded_at')
    elif thing_to_filter == "comics":
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

  
        media_files = MediaFile.objects.filter(character__name__icontains=string, hide=False).order_by('-uploaded_at')
        
        comics = Comic.objects.filter(character__name__icontains=string, hide=False).order_by('-uploaded_at')

    # Combinar y ordenar todos por fecha de subida
        combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )
    # Obtener el contexto de la sidebar
        sidebar_context = get_sidebar_context()
        context = {
            'media_files': combined_media,
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
from django.shortcuts import render
from yt_dlp import YoutubeDL
import imageio_ffmpeg

def download_video(request):
    context = {}

    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            try:
                output_dir = 'media'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'ffmpeg_location': ffmpeg_path,
                    'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
                    'postprocessors': [
                        {
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4'
                        }
                    ],
                }

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    final_filename = os.path.splitext(filename)[0] + '.mp4'

                    context['title'] = info.get('title', 'Video descargado')
                    context['filename'] = final_filename

            except Exception as e:
                context['error'] = f"⚠️ Ocurrió un error al descargar el video: {str(e)}"

    return render(request, 'index/download.html', context)






