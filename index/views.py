import datetime
from io import BytesIO
from pyexpat.errors import messages
import subprocess
from typing import Counter
from django.utils.formats import date_format
from django.contrib.auth import authenticate, login
from django.core.files import File
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
import os
import re
from django.shortcuts import render
from yt_dlp import YoutubeDL
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from django.urls import reverse
import urllib
from db.models import *
from .forms import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
import os
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator

from django.http import FileResponse, HttpResponse, HttpResponseNotFound
from django.conf import settings
from itertools import chain

import requests
import json
import time
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
import json




@csrf_exempt
def error_500(request):
    try:
        raise Exception("Error simulado para probar la vista 500.")
    except Exception as e:
        return render(request, 'index/500.html', {
            'exception': e,
        }, status=500)

def error_404(request, exception):
    return render(request, 'index/404.html', {
        'exception': exception,
    }, status=404)

def get_top_items(model, related_fields, limit=5):
    annotations = [Count(field) for field in related_fields]
    queryset = model.objects.annotate(
        num_mediafiles=sum(annotations)
    ).order_by('-num_mediafiles')[:limit]
    return queryset

def get_sidebar_context():
    return {
        'popular_tags': get_top_items(Tags, ['mediafile', 'comic']),
        'popular_artists': get_top_items(Artist, ['mediafile', 'comic']),
        'popular_characters': get_top_items(Character, ['mediafile', 'comic']),
        'popular_games': get_top_items(Game, ['mediafile', 'comic']),
    }

@login_required(login_url='/login/')
def index(request):
    user = request.user
    limit = 12
    media_files_qs = MediaFile.objects.order_by('-uploaded_at')[:limit]
    comics_qs = Comic.objects.order_by('-uploaded_at')[:limit]
    media_files = list(media_files_qs)
    comics = list(comics_qs)
    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )[:12]
    sidebar_context = get_sidebar_context()
    context = {
        'user': user,
        'media_files': combined_media,
        **sidebar_context
    }
    return render(request, 'index/index.html', context)

@login_required(login_url='/login/')  
def userProfileLikes(request,username,filter):

    return redirect('index:userProfile', request.user.username)

@login_required(login_url='/login/')
def userProfile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user and request.method == 'POST':
        return redirect('index:userProfile', user.username)
    if request.method == 'POST':
        form = editUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save()
            password2 = form.cleaned_data.get('password')
        
            if password2:
                auth_user = authenticate(username=updated_user.username, password=password2)
                if auth_user is not None:
                    login(request, auth_user)

            return redirect('index:userProfile', updated_user.username)
        else:
            print(form.errors)
    formUser = editUserForm(instance=user)
    media_files = MediaFile.objects.filter(hide=False, user=user).prefetch_related('tags')
    comics = Comic.objects.filter(hide=False, user=user).prefetch_related('tags')
    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )
    total = len(combined_media)
    allThigs = {
        'mediafiles': user.liked_mediafiles.all()[:4],
        'artists': user.liked_artist.all()[:4],
        'comics': user.liked_comic.all()[:4],
        'characters': user.liked_character.all()[:4],
        'games': user.liked_game.all()[:4],
    }
    total_likes = sum(qs.count() for qs in allThigs.values())
    favTags = []
    for _, thing in allThigs.items():
        for item in thing:
            favTags.extend(item.tags.all())

    top5_tags = [tag for tag, _ in Counter(favTags).most_common(5)]

    sidebar_context = get_sidebar_context()

    context = {
        'combined_media': combined_media[:8],
        'mediafiles': allThigs['mediafiles'],
        'artists': allThigs['artists'],
        'comics': allThigs['comics'],
        'characters': allThigs['characters'],
        'games': allThigs['games'],
        'user': user,
        'favTags': top5_tags,
        'total_likes': total_likes,
        'formUser': formUser,
        'total':total, #se añadio el 10 para el numero total de publicaciones
        **sidebar_context
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'index/userProfilehtmx.html', context)
    else:
        # Si es una petición normal, devolvemos la página completa
        return render(request, 'index/userProfile.html', context)

@login_required(login_url='/login/')  
def toggle_like(request, model, pk):
    user = request.user

    try:
        content_type = ContentType.objects.get(model=model.lower())
        model_class = content_type.model_class()
        obj = get_object_or_404(model_class, pk=pk)
    except ContentType.DoesNotExist:
        return JsonResponse({'error': 'Modelo no válido'}, status=400)

    if obj.likes.filter(id=user.id).exists():
        obj.likes.remove(user)
        liked = False
    else:
        obj.likes.add(user)
        liked = True

    return JsonResponse({'liked': liked, 'total_likes': obj.likes.count()})

@login_required(login_url='/login/')  
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
                artist = formArtist.save(commit=False)
                artist.save()  # guarda antes de M2M
                for tag in request.POST.get('tags_selectedArtist', '').split(','):
                    if tag.strip():
                        obj, created = Tags.objects.get_or_create(name=tag.strip().upper())
                        artist.tags.add(obj)

                        if created:
                            print(f"🔹 Nueva tag creada: ID={obj.id}, Nombre='{obj.name}'")
                        else:
                            print(f"✅ Tag existente encontrada: ID={obj.id}, Nombre='{obj.name}'")

                return redirect('index:adminPage')


        elif form_type == 'user_form':
            username = request.POST.get("username")
            password = request.POST.get("password")
            staff = request.POST.get("is_staff") == 'on'
            superuser = request.POST.get("is_superuser") == 'on'
        
            try:
                user = User.objects.get(username=username)
                if password:
                    user.set_password(password)
                    user.is_staff = staff
                user.is_superuser = superuser
                user.save()
        
            except User.DoesNotExist:
                print("normal")
            formUser = addUserForm(request.POST, request.FILES)
            if formUser.is_valid():
                    user = formUser.save(commit=False)
                    if password:
                        user.set_password(password)
                    user.is_staff = staff
                    user.is_superuser = superuser
                    user.save()
        
            return redirect('index:adminPage')

        elif form_type == 'game_form':
            formGame = addGameForm(request.POST, request.FILES)
            if formGame.is_valid():
                game = formGame.save(commit=False)
                game.save() 
                formGame.save()
                for tag in request.POST.get('tags_selectedGame', '').split(','):
                    if tag.strip():
                        obj, created = Tags.objects.get_or_create(name=tag.strip().upper())
                        game.tags.add(obj)

                        if created:
                            print(f"🔹 Nueva tag creada: ID={obj.id}, Nombre='{obj.name}'")
                        else:
                            print(f"✅ Tag existente encontrada: ID={obj.id}, Nombre='{obj.name}'")
                return redirect('index:adminPage')
        elif form_type == 'char_form':
            formChar = addCharsForm(request.POST, request.FILES)
            if formChar.is_valid():
                char = formChar.save(commit=False)
                char.save()
                for tag in request.POST.get('tags_selectedChar', '').split(','):
                    if tag.strip():
                        obj, created = Tags.objects.get_or_create(name=tag.strip().upper())
                        char.tags.add(obj)

                        if created:
                            print(f"🔹 Nueva tag creada: ID={obj.id}, Nombre='{obj.name}'")
                        else:
                            print(f"✅ Tag existente encontrada: ID={obj.id}, Nombre='{obj.name}'")
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
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'index/adminPagehtmx.html', context)
    else:
        # Si es una petición normal, devolvemos la página completa
        return render(request, 'index/adminPage.html', context)
    
@login_required(login_url='/login/')
def navbarFilterHeader(request):
    thing_to_filter = request.GET.get('filter')
    page_number = request.GET.get('page')

    if thing_to_filter == "Artistas":
        queryset = Artist.objects.all() 
    elif thing_to_filter == "Juegos":
        queryset = Game.objects.all()
    elif thing_to_filter == "Personajes":
        queryset = Character.objects.all()
    elif thing_to_filter == "Videos":
        queryset = MediaFile.objects.filter(hide=False).order_by('-uploaded_at')
    elif thing_to_filter == "Comics":
        queryset = Comic.objects.filter(hide=False).order_by('-uploaded_at')
    else:
        queryset = MediaFile.objects.filter(hide=False).order_by('-uploaded_at')

    paginator = Paginator(queryset, 24) 
    
    try:
        page_obj = paginator.get_page(page_number)
    except Exception:
        page_obj = paginator.get_page(1)

    sidebar_context = get_sidebar_context()

    context = {
        'media_files': page_obj.object_list, 
        'page_obj': page_obj,
        'filter_selected': thing_to_filter,
        **sidebar_context
    }

    return render(request, 'index/navbarFilterHeader.html', context)

@login_required(login_url='/login/')    
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


@login_required(login_url='/login/')  
def multi_search_results(request):
    query = request.GET.get("q", "").strip()
    print(query)
    if query == "":
        
            return redirect('index:index')
   
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
    print(combined_results)
    context = {
        'results': combined_results,
        'search_terms': terms,
        'media_files': media_files_all,  # si esto es solo para sidebar, puedes renombrarlo
        **sidebar_context
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'index/multi_search_resultshtmx.html', context)
    else:
        # Si es una petición normal, devolvemos la página completa
        return render(request, 'index/multi_search_results.html', context)
    



@login_required(login_url='/login/')  
def deleteComic(request,id):
    
    com = Comic.objects.get(id=id)
    com.delete()
    return redirect('index:index')  

@login_required(login_url='/login/')  
def deleteVideo(request,id):
    com = MediaFile.objects.get(id=id)
    com.delete()
    return redirect('index:index')  

@login_required(login_url='/login/')  
def deleteComicImage(request, id):
    com = ComicPage.objects.get(id=id)
    comic_id = com.comic.id  
    com.delete()
    return redirect('index:watchComic', comic_id)

@login_required(login_url='/login/')
def watchVideo(request, id):
    mediafile = get_object_or_404(MediaFile, id=id)
    formVideo = uploadFileForm(instance=mediafile)
    form = addComentariosForm()
    if request.method == 'POST':
        if 'update_video' in request.POST:
            formVideo = uploadFileForm(request.POST, request.FILES, instance=mediafile)
            if formVideo.is_valid():
                formVideo.save()
                mediafile = formVideo.instance
                if hasattr(mediafile, 'tags'):
                    mediafile.tags.clear()
                    for tag in request.POST.get('tags_selectedArtist', '').split(','):
                        tag = tag.strip()
                        if tag:
                            obj, _ = Tags.objects.get_or_create(name=tag.upper())
                            mediafile.tags.add(obj)
                return redirect('index:watchVideo', mediafile.id)
        elif 'comentario' in request.POST:
            form_comentario = addComentariosForm(request.POST, request.FILES)
            if form_comentario.is_valid():
                c = form_comentario.save(commit=False)
                c.usuario = request.user
                c.mediaFileID = mediafile
                c.save()
                # Pasamos el objeto 'comic' directamente sin url ni tipo
                procesar_menciones(
                    comentario_texto=c.comentario,
                    autor=request.user,
                    contenido_obj=mediafile
                )
                return redirect('index:watchVideo', mediafile.id)
         
                  
    is_audio = False
    if mediafile.file.name.lower().endswith('.mp3'):
        is_audio = True        
    mediafile.liked_by_user = request.user.is_authenticated and mediafile.likes.filter(id=request.user.id).exists()
    comentarios = Comentario.objects.filter(mediaFileID=mediafile)
    comentarios = reversed(comentarios)
    sidebar_data = get_sidebar_context()
    
    return render(request, 'index/watchVideo.html', {
        'mediafile': mediafile,
        'comentarios': comentarios,
        'form': form,
        'formVideo': formVideo,
            'is_audio': is_audio,
                    'MEDIA_URL': settings.MEDIA_URL,


        **sidebar_data,
    })

@login_required(login_url='/login/')
def watchComic(request, id):
    comic = get_object_or_404(Comic, id=id)
    form_comentario = addComentariosForm()
    form_page = ComicPageForm()
    formComic = UploadComicForm(instance=comic)
    if request.method == 'POST':
        if 'update_comic' in request.POST:
            formComic = UploadComicForm(request.POST, request.FILES, instance=comic)
            if formComic.is_valid():
                formComic.save()
                mediafile = formComic.instance
                if hasattr(mediafile, 'tags'):
                    mediafile.tags.clear()
                    for tag in request.POST.get('tags_selectedArtist', '').split(','):
                        tag = tag.strip()
                        if tag:
                            obj, _ = Tags.objects.get_or_create(name=tag.upper())
                            mediafile.tags.add(obj)
               

                return redirect('index:watchComic', comic.id)
        elif 'comentario' in request.POST:
            form_comentario = addComentariosForm(request.POST)
            if form_comentario.is_valid():
                    c = form_comentario.save(commit=False)
                    c.usuario = request.user
                    c.comicID = comic
                    c.save()

                    # Pasamos el objeto 'comic' directamente sin url ni tipo
                    procesar_menciones(
                        comentario_texto=c.comentario,
                        autor=request.user,
                        contenido_obj=comic
                    )

                    return redirect('index:watchComic', comic.id)



        images = request.FILES.getlist('images')
        if images:
            current = ComicPage.objects.filter(comic=comic).count()
            for i, img in enumerate(images, start=1):
                ComicPage(comic=comic, image=img, order=current + i).save()
            file_url = request.build_absolute_uri(reverse('index:watchComic', args=[comic.id]))
                
            texto = (
    f"🎬 <b>¡{len(images)} Nuevas imagenes subidas!</b>\n"
    f"📤 <i>Cortesía de</i> <b>{comic.user}</b>\n\n"
    f"📎 <b>Nombre:</b> <a href='{file_url}'>{comic.name}</a>\n"
    f"📺 <i>Haz clic en el nombre para verlo o descargarlo.</i>\n\n"
    f"🔞 <i>Contenido variado: anime, series, y más...</i>"
)
            # construye image_url absoluto si existe
            if hasattr(comic, 'image') and comic.image:
                image_path = comic.image.path  # <-- Path local físico
                print(image_path)
            else:
                image_path = None

            if image_path:
                with Image.open(image_path) as img:
                    img.thumbnail((1280, 1280))
                    temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                    img.save(temp, format='JPEG')
                    temp.close()
                    image_path = temp.name  # esto ya es un path que puedes mandar

            print('DEBUG: enviando Telegram', texto, image_path)
            resp = enviar_telegram_mensaje(texto, image_path)
            print('DEBUG: respuesta Telegram', resp)
            return redirect('index:watchComic', comic.id)
    comic.liked_by_user = request.user.is_authenticated and comic.likes.filter(id=request.user.id).exists()
    comentarios = Comentario.objects.filter(comicID=comic)
    comentarios = reversed(comentarios)
    comic_pages = ComicPage.objects.filter(comic=comic).order_by('order')
    sidebar_data = get_sidebar_context()
    return render(request, 'index/watchComic.html', {
        'mediafile':    comic,
        'comentarios':  comentarios,
        'comic_pages':  comic_pages,
        'form':         form_comentario,
        'form_page':    form_page,
        'formComic':    formComic,
        **sidebar_data
    })

def procesar_menciones(comentario_texto, autor, contenido_obj):
    print("📝 Texto del comentario:", comentario_texto)
    menciones = re.findall(r'@(\w+)', comentario_texto)
    print("🔍 Menciones encontradas:", menciones)

    if contenido_obj is None:
        print("⚠️ No se proporcionó un objeto de contenido válido.")
        return

    content_type = ContentType.objects.get_for_model(contenido_obj.__class__)
    object_id = contenido_obj.id

    for username in menciones:
        try:
            destinatario = User.objects.get(username=username)
            print(f"👤 Usuario encontrado: {destinatario.username}")

            if destinatario == autor:
                print("⚠️ Usuario se mencionó a sí mismo, se omite")
                continue

            Notificacion.objects.create(
                destinatario=destinatario,
                emisor=autor,
                mensaje=f"📢 {autor.username} te mencionó en un comentario: {comentario_texto}",
                content_type=content_type,
                object_id=object_id
            )
            print(f"✅ Notificación creada para {destinatario.username}")

        except User.DoesNotExist:
            print(f"❌ Usuario '{username}' no encontrado")
        except Exception as e:
            print(f"❌ Error inesperado al crear la notificación: {e}")

#@login_required(login_url='/login/')
def viewDownloadedVideos(request):
    media_path = settings.MEDIA_ROOT
    archivos = []

    if os.path.exists(media_path):
        archivos = [f for f in os.listdir(media_path)
                    if os.path.isfile(os.path.join(media_path, f))]

    archivos.sort(reverse=True)
    paginator = Paginator(archivos, 10)  # 10 archivos por página

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index/viewDownloadedVideos.html', {
        'archivos': page_obj,
        'MEDIA_URL': settings.MEDIA_URL,
    })

@login_required(login_url='/login/')
def deleteDownloadedVideo(request, filename):
    if request.method == 'POST':
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                time.sleep(0.5)  # Espera para que el navegador libere el archivo
                os.remove(file_path)
            except PermissionError:
                return HttpResponse("No se pudo eliminar el archivo por falta de permisos", status=403)
            return redirect('index:viewDownloadedVideos')
        return HttpResponse("Archivo no encontrado", status=404)
    return HttpResponse("Método no permitido", status=405)


@login_required(login_url='/login/')
def uploadDownloadedVideo(request, filename):
    if request.method == 'POST':
        local_filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        if not os.path.exists(local_filepath):
            return redirect('index:viewDownloadedVideos')

        with open(local_filepath, 'rb') as f:
            uploaded_file = File(f, name=filename)

            data = {
                'name': os.path.splitext(filename)[0],
                'user': request.user.id,
                'artist': '',
                'game': '',
                'character': '',
            }
            
            form = uploadFileForm(data, files={'file': uploaded_file})

            if form.is_valid():
                media = form.save(commit=False)
                media.user = request.user
                
                base_name, ext = os.path.splitext(media.file.name)
                ext = ext.lower()
                is_audio = ext in AUDIO_FORMATS

                upload_dir = datetime.datetime.now().strftime("media_files/%Y%m%d/")
                
                if is_audio:
                    final_name_base = f"{base_name}{ext}"
                else:
                    final_name_base = f"{base_name}.mp4"
                
                final_name = final_name_base

                count = 1
                while default_storage.exists(os.path.join(upload_dir, final_name)):
                    if is_audio:
                        final_name = f"{os.path.splitext(base_name)[0]}_{count}{ext}"
                    else:
                        final_name = f"{os.path.splitext(base_name)[0]}_{count}.mp4"
                    count += 1
                
                final_path_in_storage = os.path.join(upload_dir, final_name)
                media.file.name = final_path_in_storage
                
                media.save()
                form.save_m2m()

                for tag in request.POST.get('tags_selectedVideo', '').split(','):
                    if tag.strip():
                        obj, _ = Tags.objects.get_or_create(name=tag.strip().upper())
                        media.tags.add(obj)

                file_url = request.build_absolute_uri(reverse('index:watchVideo', args=[media.id]))
                texto = (
                    f"🎬 <b>¡Nuevo video subido!</b>\n"
                    f"📤 <i>Cortesía de</i> <b>{media.user}</b>\n\n"
                    f"📎 <b>Nombre:</b> <a href='{file_url}'>{media.name}</a>\n"
                    f"📺 <i>Haz clic en el nombre para verlo o descargarlo.</i>\n\n"
                    f"🔞 <i>Contenido variado: anime, series, y más...</i>"
                )
                
                image_path = None
                
                if media.image and hasattr(media.image, 'path') and os.path.exists(media.image.path):
                     try:
                        with Image.open(media.image.path) as img:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            max_size = (1280, 1280)
                            img.thumbnail(max_size)
                            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                                img.save(temp_img.name, format='JPEG', quality=85)
                                image_path = temp_img.name
                     except Exception as e:
                        print(f"❌ Error al procesar la imagen para Telegram: {e}")

                enviar_telegram_mensaje(texto, image_path)

                return redirect('index:index')
            else:
                print(f"Errores del formulario: {form.errors}")
                return redirect('index:viewDownloadedVideos')

    return redirect('index:viewDownloadedVideos')
@login_required(login_url='/login/')
def detailsAbout(request, filtro, valor):
    sidebar_context = get_sidebar_context()

    # helper para saber si el user ha likeado un objeto
    def mark_liked(obj):
        # si no está autenticado, siempre False
        if not request.user.is_authenticated:
            obj.liked_by_user = False
        else:
            # asume que cada modelo tiene el M2M .likes
            obj.liked_by_user = obj.likes.filter(id=request.user.id).exists()
        return obj

    if filtro == "character":
        resultado = get_object_or_404(Character, name=valor)
        media_files = MediaFile.objects.filter(character=resultado)
        comics      = Comic.objects.filter(character=resultado)

    elif filtro=="artist":
        resultado   = get_object_or_404(Artist, name=valor)
        media_files = MediaFile.objects.filter(artist=resultado)
        comics      = Comic.objects.filter(artist=resultado)

    elif filtro=="game":
        resultado   = get_object_or_404(Game, name=valor)
        media_files = MediaFile.objects.filter(game=resultado)
        comics      = Comic.objects.filter(game=resultado)

    else:
        return render(request, 'index/detailsAbout.html', {
            'mensaje': "Filtro no reconocido",
            **sidebar_context
        })

    # combina y ordena
    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )

    # marca liked_by_user en resultado y en cada item de combined_media
    resultado = mark_liked(resultado)
    combined_media = [mark_liked(obj) for obj in combined_media]

    # arma el contexto
    context = {
        'contenido': combined_media,
        'resultado': resultado,
        'filtro': filtro,
        'valor': valor,
        **sidebar_context,
    }

    return render(request, 'index/detailsAbout.html', context)


@require_POST

@login_required(login_url='/login/')
def ajax_add_comment(request, id):
    form = addComentariosForm(request.POST)

    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.usuario = request.user

        tipo_objeto = request.POST.get('tipo_objeto')  # <<<<<< Recibimos lo que mandamos en el fetch
        
        if tipo_objeto == 'comic':
            comentario.comicID_id = id
        elif tipo_objeto == 'mediafile':
            comentario.mediaFileID_id = id
        else:
            return JsonResponse({'error': 'Tipo de objeto inválido'}, status=400)

        comentario.save()

        fecha_formateada = comentario.uploaded_at.strftime("%d de %B de %Y a las %H:%M")

        return JsonResponse({
    'usuario': str(comentario.usuario),
    'fecha': fecha_formateada,
    'texto': comentario.comentario
})

    return JsonResponse({'error': 'Comentario no válido'}, status=400)


def stream_video(request, id):
    try:
        media = MediaFile.objects.get(id=id)
    except MediaFile.DoesNotExist:
        return HttpResponseNotFound("Archivo no encontrado")

    # Ruta absoluta en disco
    path = os.path.join(settings.MEDIA_ROOT, media.file.name)

    if not os.path.exists(path):
        return HttpResponseNotFound("Archivo no encontrado en disco")

    range_header = request.headers.get('Range', '')
    if range_header:
        start, end = range_header.replace('bytes=', '').split('-')
        start = int(start)
        end = int(end) if end else os.path.getsize(path) - 1
        length = end - start + 1

        with open(path, 'rb') as f:
            f.seek(start)
            data = f.read(length)

        response = HttpResponse(data, status=206, content_type='video/mp4')
        response['Content-Range'] = f'bytes {start}-{end}/{os.path.getsize(path)}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        return response

    return FileResponse(open(path, 'rb'), content_type='video/mp4')


@login_required(login_url='/login/')  
def filtered_media(request, filter_type, string):
    sidebar_context = get_sidebar_context()

 
    filter_map = {
    'tag': ('tags__name__iexact',),  # ← clave aquí
    'artist': ('artist__name__iexact',),
    'character': ('character__name__iexact',),
    'game': ('game__name__iexact',)
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

AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.aac', '.flac']

def can_upload_check(user):
    return user.is_authenticated and getattr(user, 'can_upload', False)

@user_passes_test(can_upload_check, login_url='/login/')
@login_required(login_url='/login/')
def uploadFile(request):

  
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'video':
            form = uploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                media = form.save(commit=False)
                media.user = request.user

                uploaded_file = request.FILES['file']
                base_name, ext = os.path.splitext(uploaded_file.name)
                ext = ext.lower()
                is_audio = ext in AUDIO_FORMATS

                upload_dir = datetime.datetime.now().strftime("media_files/%Y%m%d/")
                os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)

                # Define el nombre final según tipo
                if is_audio:
                    final_name = f"{base_name}{ext}"
                else:
                    final_name = f"{base_name}.mp4"

                count = 1
                while default_storage.exists(os.path.join(upload_dir, final_name)):
                    if is_audio:
                        final_name = f"{base_name}_{count}{ext}"
                    else:
                        final_name = f"{base_name}_{count}.mp4"
                    count += 1

 
                uploaded_file.name = final_name
                media.file = uploaded_file



                if 'image' in request.FILES:
                    media.image = request.FILES['image']

                media.save()
                form.save_m2m()

                for tag in request.POST.get('tags_selectedVideo', '').split(','):
                    if tag.strip():
                        obj, _ = Tags.objects.get_or_create(name=tag.strip().upper())
                        media.tags.add(obj)

                file_url = request.build_absolute_uri(reverse('index:watchVideo', args=[media.id]))
                texto = (
                    f"🎬 <b>¡Nuevo video subido!</b>\n"
                    f"📤 <i>Cortesía de</i> <b>{media.user}</b>\n\n"
                    f"📎 <b>Nombre:</b> <a href='{file_url}'>{media.name}</a>\n"
                    f"📺 <i>Haz clic en el nombre para verlo o descargarlo.</i>\n\n"
                    f"🔞 <i>Contenido variado: anime, series, y más...</i>"
                )

                image_path = None

                if media.image and hasattr(media.image, 'path') and os.path.exists(media.image.path):
                    try:
                        with Image.open(media.image.path) as img:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')

                            max_size = (1280, 1280)
                            img.thumbnail(max_size)

                            # Guardar imagen temporal en JPEG
                            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                                img.save(temp_img.name, format='JPEG', quality=85)
                                image_path = temp_img.name
                    except Exception as e:
                        print(f"❌ Error al procesar la imagen para Telegram: {e}")

                print('DEBUG: enviando Telegram', texto, image_path)
                resp = enviar_telegram_mensaje(texto, image_path)
                print('DEBUG: respuesta Telegram', resp)

                return redirect('index:index')

        elif form_type == 'comic':
            formComic = UploadComicForm(request.POST)
            if formComic.is_valid():
                comic = formComic.save(commit=False)
                images = request.FILES.getlist('comicImages')
                print("DEBUG: imágenes recibidas", images)
                comic.image = images[0]
                comic.user = request.user
                comic.save()
                formComic.save_m2m()
            
                for index, image in enumerate(request.FILES.getlist('comicImages')):
                    ComicPage.objects.create(comic=comic, image=image, order=index)

            
                for tag in request.POST.get('tags_selectedComic', '').split(','):
                    if tag.strip():
                        obj, _ = Tags.objects.get_or_create(name=tag.strip().upper())
                        comic.tags.add(obj)
            
                file_url = request.build_absolute_uri(reverse('index:watchComic', args=[comic.id]))
                texto = (
                    f"🎬 <b>¡Nuevo imagén subida!</b>\n"
                    f"📤 <i>Cortesía de</i> <b>{comic.user}</b>\n\n"
                    f"📎 <b>Nombre:</b> <a href='{file_url}'>{comic.name}</a>\n"
                    f"📺 <i>Haz clic en el nombre para verlo.</i>\n\n"
                    f"🔞 <i>Contenido variado: anime, series, y más...</i>"
                )
            
                image_path = None
                temp_image_path = None
            
                if comic.image:
                    try:
                        with Image.open(comic.image.path) as img:
                            width, height = img.size
                            if width > 0 and height > 0:
                                if img.mode != "RGB":
                                    img = img.convert("RGB")
                                temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                                img.save(temp_file.name, format="JPEG")
                                temp_image_path = temp_file.name
                                image_path = temp_image_path
                            else:
                                print(f"❌ Imagen con dimensiones inválidas: {width}x{height}")
                    except Exception as e:
                        print(f"❌ Error al abrir la imagen: {e}")
            
                print('DEBUG: enviando Telegram', texto, image_path)
                resp = enviar_telegram_mensaje(texto, image_path)
                print('DEBUG: respuesta Telegram', resp)
                
                return redirect('index:index')
    # GET o errores: reconstruir context original
    form = uploadFileForm()
    formComic = UploadComicForm()
    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at')
    sidebar_context = get_sidebar_context()
    context = {
        'form': form,
        'formComic': formComic,
        'media_files': media_files,
        **sidebar_context
    }
    return render(request, 'index/uploadFile.html', context)


def enviar_telegram_mensaje(texto, image_path=None):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_GROUP_CHAT_ID

    # ⚙️ CAMBIO AQUÍ (Usa esto si estás en LOCAL + NGROK)
    # Ejemplo: ngrok_url = "https://d3f4-189-204-123-123.ngrok-free.app"
    # ⚠️ Este valor debería idealmente venir de settings o una variable de entorno
    ngrok_url = "https://d3f4-189-204-123-123.ngrok-free.app"

    # 🏠 Modo LOCAL (sin ngrok, puede fallar si image_path no es accesible desde fuera)
    is_localhost = "127.0.0.1" in texto or "localhost" in texto

    # ☝️ Si usas image_url generado desde Django (media.image.url), reemplaza 127.0.0.1 por tu ngrok
    if is_localhost:
        texto = texto.replace("http://127.0.0.1:8000", ngrok_url)

    if image_path and os.path.exists(image_path):
        # 🖼️ Enviar imagen + texto juntos usando sendPhoto
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            with open(image_path, 'rb') as img:
                files = {'photo': img}
                data = {
                    'chat_id': chat_id,
                    'caption': texto,
                    'parse_mode': 'HTML'
                }
                r = requests.post(url, data=data, files=files)
                res = r.json()
                return {'ok': True, 'combined_msg': res}
        except Exception as e:
            return {'ok': False, 'error': f'Error en sendPhoto: {e}'}
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': texto,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        try:
            r = requests.post(url, data=data)
            res = r.json()
            return {'ok': True, 'text_msg': res}
        except Exception as e:
            return {'ok': False, 'error': f'Error en sendMessage: {e}'}


@login_required(login_url='/login/')
def edit_objeto(request, tipo, pk):
    modelo_map = {
        'character': (Character, addCharsForm),
        'artist': (Artist, addArtistForm),
        'game': (Game, addGameForm),
    }
    if tipo not in modelo_map:
        return redirect('index:index')

    Modelo, Formulario = modelo_map[tipo]
    instancia = get_object_or_404(Modelo, pk=pk)

    if request.method == 'POST':
        form = Formulario(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            instancia = form.save(commit=False)
            
            if tipo == 'artist':
                redes_disponibles = [
                    'facebook', 'twitter', 'instagram', 'youtube', 
                    'tiktok', 'onlyfans', 'rule34', 'patreon', 'coomer'
                ]
                social_data = {}
                for red in redes_disponibles:
                    valor = request.POST.get(f'{red}_url', '').strip()
                    if valor:
                        social_data[red] = valor
                
                instancia.social_media = social_data

            instancia.save()
            form.save_m2m()

            if hasattr(instancia, 'tags'):
                instancia.tags.clear()
                tags_data = request.POST.get('tags_selectedArtist', '')
                for tag in tags_data.split(','):
                    tag_name = tag.strip()
                    if tag_name:
                        obj, _ = Tags.objects.get_or_create(name=tag_name.upper())
                        instancia.tags.add(obj)

            return redirect('index:detailsAbout', filtro=tipo, valor=instancia.name)
    else:
        form = Formulario(instance=instancia)

    sidebar_context = get_sidebar_context()
    context = {
        'form': form,
        'tipo': tipo,
        'instancia': instancia,
        **sidebar_context
    }
    return render(request, 'index/edit_objeto.html', context)

@login_required
def tags_suggest(request):
    q = request.GET.get('q', '')
    tags = Tags.objects.filter(name__icontains=q).values_list('name', flat=True)[:10]
    return JsonResponse(list(tags), safe=False)

def get_items(request, type):
    model_map = {
        'tags': Tags,
        'artists': Artist,
        'chars': Character,
        'users': User,
        'games': Game
    }
    Model = model_map.get(type)

    if type == "users":
        modelTypeName = "username"
    else:    
        modelTypeName = "name"

    if Model:
        is_admin = request.user.is_authenticated and request.user.is_staff and request.user.is_superuser
        data = list(Model.objects.all().values('id', modelTypeName))

        # Añadir la bandera para el frontend
        for item in data:
            item['current_user_is_admin'] = is_admin

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Invalid type'}, status=400)

@csrf_exempt
@login_required(login_url='/login/')
def delete_item(request, type, id):
    if not (request.user.is_superuser and request.user.is_staff):
        return JsonResponse({'error': 'Acceso no autorizado'}, status=403)

    model_map = {
        'tags': Tags,
        'artists': Artist,
        'chars': Character,
        'users': User,
        'games': Game
    }

    Model = model_map.get(type)
    if Model and request.method == 'DELETE':
        if Model.objects.count() <= 1:
            return JsonResponse({'error': 'No se puede eliminar el último elemento'}, status=400)
        else:
            Model.objects.filter(id=id).delete()
            return JsonResponse({'success': True})

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)




def safe_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    return name.strip('_')


#@login_required(login_url='/login/')  
def videoDownloader(request):
    context = {}
    sidebar_context = get_sidebar_context()

    if request.method == 'POST':
        url = request.POST.get('url')
        download_type = request.POST.get('download_type', 'video')

        if url:
            try:
                output_dir = 'media'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'
                
                is_direct_link = any(url.lower().endswith(ext) or ext + "?" in url.lower() for ext in ['.mp4', '.mkv', '.avi', '.mov', '.mp3'])

                if is_direct_link and download_type == 'video':
                    clean_title = safe_filename(url.split('/')[-1].split('?')[0])
                    if not clean_title:
                        clean_title = "descarga_directa"
                    
                    final_filename = f"{clean_title}"
                    full_path = os.path.join(output_dir, final_filename)

                    if os.path.exists(full_path):
                        context['title'] = clean_title
                        context['filename'] = final_filename
                        context['already_downloaded'] = True
                    else:
                        with requests.get(url, stream=True) as r:
                            r.raise_for_status()
                            with open(full_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        context['title'] = clean_title
                        context['filename'] = final_filename
                else:
                    with YoutubeDL({'quiet': True}) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info.get('title', 'video')
                        ext = 'mp3' if download_type == 'audio' else info.get('ext', 'mp4')
                        clean_title = safe_filename(title)
                        final_filename = f"{clean_title}_{download_type}.{ext}"
                        full_path = os.path.join(output_dir, final_filename)

                    if os.path.exists(full_path):
                        context['title'] = title
                        context['filename'] = final_filename
                        context['already_downloaded'] = True
                    else:
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
                            ydl_opts.update({'format': 'bestvideo+bestaudio/best'})

                        with YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            downloaded = ydl.prepare_filename(info)
                            if download_type == 'audio':
                                downloaded = os.path.splitext(downloaded)[0] + '.mp3'
                            
                            if os.path.exists(downloaded) and downloaded != full_path:
                                if os.path.exists(full_path):
                                    os.remove(full_path)
                                os.rename(downloaded, full_path)

                            context['title'] = title
                            context['filename'] = final_filename

            except Exception as e:
                context['error'] = f"⚠️ Error al descargar: {str(e)}"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'filename': context.get('filename'),
                'already_downloaded': context.get('already_downloaded', False),
                'error': context.get('error')
            })

    context.update(sidebar_context)
    return render(request, 'index/videoDownloader.html', context)

import os

import os

@login_required(login_url='/login/')
def recentPosts(request):
    posts_list = Post.objects.select_related('user').prefetch_related('likes', 'images').filter(hide=False).order_by('-uploaded_at')
    sidebar_context = get_sidebar_context()
    
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    video_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
    user = request.user

    for post in page_obj:
        post.liked_by_user = post.likes.filter(id=user.id).exists()
        for media in post.images.all():
            extension = os.path.splitext(media.image.name)[1].lower()
            media.is_video = extension in video_extensions
            
    context = {
        'page_obj': page_obj, 
        **sidebar_context
    } 
    return render(request, 'index/recentPosts.html', context)

@login_required(login_url='/login/')  
def editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
    return redirect('index:recentPosts')



@login_required(login_url='/login/')  
def eliminar_post(request,id):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('index:recentPosts')

@login_required(login_url='/login/')  
def createPost(request):
    sidebar_context = get_sidebar_context()

    if request.method == 'POST':
      form = PostForm(request.POST, request.FILES)
      imagenes = request.FILES.getlist('imagenes')

      if len(imagenes) > 5:
          form.add_error(None, "Solo puedes subir un máximo de 5 imágenes.")
      elif form.is_valid():
          post = form.save(commit=False)
          post.user = request.user
          post.save()
          form.save_m2m()

          for imagen in imagenes:
              PostImage.objects.create(post=post, image=imagen)

          return redirect('index:recentPosts')

    else:
        form = PostForm()

    context = {
        'form': form,
        **sidebar_context
    }
    return render(request, 'index/createPost.html', context)

@login_required(login_url='/login/')  
def notificaciones_count(request):
    cantidad = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
    return JsonResponse({'count': cantidad})

@login_required(login_url='/login/')  
def obtener_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user, leida=False).order_by('-fecha')[:10]
    data = []

    for n in notificaciones:
        imagen = None
        url = None

        # Obtener objeto relacionado
        contenido = n.contenido_objeto
        if contenido:
            model_name = contenido._meta.model_name

            if model_name == 'comic':
                # Construir url para el comic
                url = reverse('index:watchComic', args=[contenido.id])
                if hasattr(contenido, 'image') and contenido.image:
                    imagen = contenido.image.url

            elif model_name == 'mediafile':
                # Construir url para el mediafile
                url = reverse('index:watchVideo', args=[contenido.id])
                if hasattr(contenido, 'image') and contenido.image:
                    imagen = contenido.image.url
        
        # Si no tiene objeto relacionado o no tiene URL, url queda None o ""
        if not url:
            url = ""

        data.append({
            'id': n.id,
            'mensaje': n.mensaje,
            'leida': n.leida,
            'fecha': n.fecha.strftime('%d/%m/%Y %H:%M'),
            'url': url,
            'imagen': imagen,
        })

    return JsonResponse({'notificaciones': data})

@login_required(login_url='/login/')  
@require_POST
def marcar_leida(request):
    notificacion_id = request.POST.get('id')
    print(notificacion_id)
    try:
        noti = Notificacion.objects.get(id=notificacion_id, destinatario=request.user)
        noti.leida = True
        noti.save()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificación no encontrada'}, status=404)

@login_required(login_url='/login/')  
def pastNotifications(request):
    sidebar_context = get_sidebar_context()
    user = request.user

    noti = Notificacion.objects.filter(destinatario=user).order_by('-fecha')[:9]
    #print(noti)
    for n in noti:
        # Añadir imagen si existe
        if n.contenido_objeto and hasattr(n.contenido_objeto, 'image'):
              
            try:
                n.imagen_url = n.contenido_objeto.image.url
              
            except Exception:
                n.imagen_url = None
        else:
            n.imagen_url = None

        # Construir URL para "Ver más" según el tipo de contenido relacionado
        n.url_objeto = None
        if n.contenido_objeto:
            model_name = n.contenido_objeto._meta.model_name
            if model_name == 'comic':
                n.url_objeto = reverse('index:watchComic', args=[n.contenido_objeto.id])
            elif model_name == 'mediafile':
                n.url_objeto = reverse('index:watchVideo', args=[n.contenido_objeto.id])  # Cambia según tu URL real

    context = {
        **sidebar_context,
        'user': user,
        'noti': noti,
    }
    return render(request, 'index/allNotifications.html', context)

def load_audio(request, media_id):
    media = get_object_or_404(MediaFile, id=media_id)
    context = {
        'id_media':media.id,
        'audio_url': media.file.url,
        'media_name': media.name,
        'image_url': media.image.url if media.image else None,
    }
    html = render_to_string('index/audioSource.html', context)
    return HttpResponse(html)
#def load_audio(request, media_id):
#    media = get_object_or_404(MediaFile, id=media_id)
#
#    extension = os.path.splitext(media.file.name)[1].lower()  # .mp3 o .mp4
#
#    is_video = extension == '.mp4'
#
#    context = {
#        'media_name': media.name,
#        'file_url': media.file.url,
#        'image_url': media.image.url if media.image else None,
#        'is_video': is_video,
#    }
#
#    html = render_to_string('index/audioSource.html', context)
#    return HttpResponse(html)   
@login_required(login_url='/login/')    
def allVideosHide(request):
 
    media_files = MediaFile.objects.filter(hide=True).order_by('-uploaded_at')
    comics = Comic.objects.filter(hide=True).order_by('-uploaded_at')

    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )
    sidebar_context = get_sidebar_context()

    context = {
        'combined_media': combined_media,
        **sidebar_context
    }

    return render(request, 'index/hideVids.html', context)