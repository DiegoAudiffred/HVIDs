import datetime
from io import BytesIO
from pyexpat.errors import messages
import subprocess
from typing import Counter
from django.utils.formats import date_format
from django.contrib.auth import authenticate, login
from django.core.files import File

from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from django.urls import reverse
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

from django.http import FileResponse, HttpResponse, HttpResponseNotFound
from django.conf import settings

import requests


def get_sidebar_context():
    popular_tags = Tags.objects.annotate(num_mediafiles=Count('mediafile')+Count('comic')).order_by('-num_mediafiles')[:5]

    popular_artists = Artist.objects.annotate(num_mediafiles=Count('mediafile')+Count('comic')).order_by('-num_mediafiles')[:5]

    popular_characters = Character.objects.annotate(num_mediafiles=Count('mediafile')+Count('comic')).order_by('-num_mediafiles')[:5]
    
    popular_games = Game.objects.annotate(num_mediafiles=Count('mediafile')+Count('comic')).order_by('-num_mediafiles')[:5]


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

@login_required(login_url='/login/')  # ruta de la vista login
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
    )[:15]

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

@login_required(login_url='/login/')  # ruta de la vista login
def userProfile(request,username):
    user = User.objects.get(username=username)

    if request.method == 'POST':
        print("entro")
        form = editUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save()
            password2 = form.cleaned_data.get('password')
        
            if password2:
                user = authenticate(username=updated_user.username, password=password2)
                if user is not None:
                    login(request, user)

                
            return redirect('index:userProfile', updated_user.username)
        else:
            print(form.errors)
            

    
   
    formUser = editUserForm(instance=user)

    media_files = MediaFile.objects.filter(hide=False,user=user)
    comics = Comic.objects.filter(hide=False,user=user)
    # Combinar y ordenar
    combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True
    )[:10]
    allThigs={ 'mediafiles': user.liked_mediafiles.all(),
    'artists': user.liked_artist.all(),
    'comics': user.liked_comic.all(),
    'characters': user.liked_character.all(),
    'games': user.liked_game.all(),
    }

    
    total_likes = sum(qs.count() for qs in allThigs.values())


    favTags = []
    for _, thing in allThigs.items():
        for file in thing:
            for tag in file.tags.all():
                favTags.append(tag)

    # Obtener las 5 etiquetas más comunes
    top5_tags = Counter(favTags).most_common(5)

    # Si solo quieres los objetos tag (sin las cantidades)
    top5_tags = [tag for tag, count in top5_tags]
    sidebar_context = get_sidebar_context()

    context = {
    'combined_media':combined_media,  
    'mediafiles': user.liked_mediafiles.all(),
    'artists': user.liked_artist.all(),
    'comics': user.liked_comic.all(),
    'characters': user.liked_character.all(),
    'games': user.liked_game.all(),
    'user': user,
    'favTags':top5_tags,
    'total_likes':total_likes,
    'formUser':formUser,
            **sidebar_context

}
    
    return render(request, 'index/userProfile.html', context)

@login_required(login_url='/login/')  # ruta de la vista login

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

@login_required(login_url='/login/')  # ruta de la vista login

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

    return render(request, 'index/adminPage.html', context)
@login_required(login_url='/login/')  # ruta de la vista login  
def navbarFilterHeader(request):
    thing_to_filter = request.GET.get('filter')

    if thing_to_filter == "Artistas":
        media_files = Artist.objects.all
    elif thing_to_filter == "Juegos":
        media_files = Game.objects.all
    elif thing_to_filter == "Personajes":
        media_files = Character.objects.all
    elif thing_to_filter == "Videos":
         media_files = MediaFile.objects.filter().order_by('-uploaded_at')
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



@login_required(login_url='/login/')  
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




@login_required(login_url='/login/')  
def deleteComic(request,id):
    com = Comic.objects.get(id=id)
    com.delete()
    return redirect('index:index')  # Redirigir correctamente


def deleteVideo(request,id):
    com = MediaFile.objects.get(id=id)
    com.delete()
    return redirect('index:index')  # Redirigir correctamente

def deleteComicImage(request, id):
    com = ComicPage.objects.get(id=id)
    comic_id = com.comic.id  
    com.delete()
    return redirect('index:watchComic', comic_id)



@login_required(login_url='/login/')
def watchContent(request, id):
    mediafile = get_object_or_404(MediaFile, id=id)
    formVideo = UploadElementForm(instance=mediafile)
    form = addComentariosForm()
    if request.method == 'POST':
        if 'update_video' in request.POST:
            formVideo = UploadElementForm(request.POST, request.FILES, instance=mediafile)
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
                return redirect('index:watchContent', mediafile.id)
        elif 'comentario' in request.POST:
            form = addComentariosForm(request.POST, request.FILES)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.usuario = request.user
                comentario.mediaFileID = mediafile
                comentario.save()
                return redirect('index:watchContent', mediafile.id)
    mediafile.liked_by_user = request.user.is_authenticated and mediafile.likes.filter(id=request.user.id).exists()
    comentarios = Comentario.objects.filter(mediaFileID=mediafile)
    comentarios = reversed(comentarios)
    sidebar_data = get_sidebar_context()
    return render(request, 'index/watchContent.html', {
        'mediafile': mediafile,
        'comentarios': comentarios,
        'form': form,
        'formVideo': formVideo,
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
        return render(request, 'index/filteredInfoPage.html', {
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

    return render(request, 'index/filteredInfoPage.html', context)


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


@login_required(login_url='/login/')  # ruta de la vista login

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

@login_required(login_url='/login/')
def uploadElement(request):

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'video':
            form = UploadElementForm(request.POST, request.FILES)
            if form.is_valid():
                media = form.save(commit=False)
                media.user = request.user
        
                uploaded_file = request.FILES['file']
                base_name, ext = os.path.splitext(uploaded_file.name)
                ext = ext.lower()
                upload_dir = datetime.datetime.now().strftime("media_files/%Y%m%d/")
                os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)
        
                final_name = f"{base_name}.mp4"  # fuerza mp4 al final
                count = 1
                while default_storage.exists(os.path.join(upload_dir, final_name)):
                    final_name = f"{base_name}_{count}.mp4"
                    count += 1
        
                save_path = os.path.join(settings.MEDIA_ROOT, upload_dir, final_name)
        
                if ext != ".mp4":
                    # Guardar archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_input:
                        for chunk in uploaded_file.chunks():
                            temp_input.write(chunk)
                        temp_input_path = temp_input.name
        
                    # Convertir a MP4 con ffmpeg
                    subprocess.run([
                        "ffmpeg", "-i", temp_input_path, "-c:v", "libx264", "-crf", "23", "-preset", "medium", save_path
                    ], check=True)
        
                    # Eliminar temporal
                    os.remove(temp_input_path)
        
                    # Asignar archivo convertido a media.file
                    with open(save_path, 'rb') as f:
                        media.file.save(final_name, File(f), save=False)
                    if os.path.exists(save_path):
                        os.remove(save_path)    
                else:
                    # Si ya es .mp4, guardarlo tal cual
                    uploaded_file.name = final_name
                    media.file = uploaded_file
        
                media.save()
                form.save_m2m()

                # tags
                for tag in request.POST.get('tags_selectedVideo', '').split(','):
                    if tag.strip():
                        obj, _ = Tags.objects.get_or_create(name=tag.strip().upper())
                        media.tags.add(obj)

                # notificación
              # ... dentro de uploadElement, tras media.save() y tags ...
                file_url = request.build_absolute_uri(reverse('index:watchContent', args=[media.id]))
                texto = (
    f"🎬 <b>¡Nuevo video subido!</b>\n"
    f"📤 <i>Cortesía de</i> <b>{media.user}</b>\n\n"
    f"📎 <b>Nombre:</b> <a href='{file_url}'>{media.name}</a>\n"
    f"📺 <i>Haz clic en el nombre para verlo o descargarlo.</i>\n\n"
    f"🔞 <i>Contenido variado: anime, series, y más...</i>"
)
                
                # construye image_url absoluto si existe
                if hasattr(media, 'image') and media.image:
                    image_path = media.image.path  # <-- Path local físico
                else:
                    image_path = None

                
                print('DEBUG: enviando Telegram', texto, image_path)
                resp = enviar_telegram_mensaje(texto, image_path)
                print('DEBUG: respuesta Telegram', resp)


                return redirect('index:index')

        elif form_type == 'comic':
            formComic = UploadComicForm(request.POST)
            if formComic.is_valid():
                comic = formComic.save(commit=False)
                comic.image = request.FILES.getlist('comicImages')[0]
                comic.user = request.user
                comic.save()
                formComic.save_m2m()
            
                for image in request.FILES.getlist('comicImages'):
                    ComicPage.objects.create(comic=comic, image=image)
            
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

    # GET o errores: reconstruir context original
    form = UploadElementForm()
    formComic = UploadComicForm()
    media_files = MediaFile.objects.filter(hide=False).order_by('-uploaded_at')
    sidebar_context = get_sidebar_context()
    context = {
        'form': form,
        'formComic': formComic,
        'media_files': media_files,
        **sidebar_context
    }
    return render(request, 'index/uploadElement.html', context)


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
    # Mapea tipo a modelo y formulario
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
            # guarda campos del formulario
            form.save()
            instancia = form.instance

            # si el modelo tiene campo ManyToMany 'tags', actualizarlo
            if hasattr(instancia, 'tags'):
                # opcional: limpiar etiquetas previas
                instancia.tags.clear()
                # agregar nuevas etiquetas desde el input oculto
                for tag in request.POST.get('tags_selectedArtist', '').split(','):
                    tag = tag.strip()
                    if tag:
                        obj, _ = Tags.objects.get_or_create(name=tag.upper())
                        instancia.tags.add(obj)

            return redirect('index:detailsAbout', filtro=tipo, valor=instancia.name)
    else:
        form = Formulario(instance=instancia)

    # Contexto lateral u otros datos
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


# views.py


def get_items(request, type):
    model_map = {
        'tags': Tags,
        'artists': Artist,
        'chars': Character,
        'users': User,
        'games': Game
    }
    Model = model_map.get(type)

    if type =="users":
        modelTypeName="username"
    else:    
        modelTypeName="name"

    if Model:
        data = list(Model.objects.all().values('id', modelTypeName))
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Invalid type'}, status=400)


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def delete_item(request, type, id):
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
            return JsonResponse({'error': 'No se puede eliminar el último usuario'}, status=400)
        else:          
            Model.objects.filter(id=id).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)



import os
import re
from django.shortcuts import render
from yt_dlp import YoutubeDL

def safe_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    return name.strip('_')


@login_required(login_url='/login/')  # ruta de la vista login

def download_video(request):
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

                # Obtener info sin descargar
                with YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'video')
                    ext = 'mp3' if download_type=='audio' else info.get('ext','mp4')
                    clean_title = safe_filename(title)
                    final_filename = f"{clean_title}_{download_type}.{ext}"
                    full_path = os.path.join(output_dir, final_filename)

                # Ya descargado?
                if os.path.exists(full_path):
                    context['title'] = title
                    context['filename'] = final_filename
                    context['already_downloaded'] = True
                else:
                    # Configuración de yt-dlp
                    ydl_opts = {
                        'ffmpeg_location': ffmpeg_path,
                        'noplaylist': True,
                        'quiet': True,
                        'nooverwrites': True,
                        'nopart': True,
                        'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
                    }
                    if download_type=='audio':
                        ydl_opts.update({
                            'format':'bestaudio',
                            'postprocessors':[{
                                'key':'FFmpegExtractAudio',
                                'preferredcodec':'mp3',
                                'preferredquality':'192',
                            }]
                        })
                    else:
                        ydl_opts.update({'format':'bestvideo+bestaudio/best'})

                    # Descargar
                    try:
                        with YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            downloaded = ydl.prepare_filename(info)
                            if download_type=='audio':
                                downloaded = os.path.splitext(downloaded)[0]+'.mp3'
                            if os.path.exists(downloaded) and downloaded!=full_path:
                                os.rename(downloaded, full_path)

                            context['title'] = title
                            context['filename'] = final_filename
                    except Exception:
                        # fallback
                        fallback = {
                            'format': 'bestaudio' if download_type=='audio' else 'best',
                            'noplaylist': True, 'quiet': True,
                            'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
                            'nooverwrites': True, 'nopart': True,
                        }
                        with YoutubeDL(fallback) as ydl:
                            info = ydl.extract_info(url, download=True)
                            downloaded = ydl.prepare_filename(info)
                            if download_type=='audio':
                                downloaded = os.path.splitext(downloaded)[0]+'.mp3'
                            if os.path.exists(downloaded) and downloaded!=full_path:
                                os.rename(downloaded, full_path)
                        context['title'] = title
                        context['filename'] = final_filename

            except Exception as e:
                context['error'] = f"⚠️ Error al descargar: {str(e)}"

        # Si AJAX, devolver JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'filename': context.get('filename'),
                'already_downloaded': context.get('already_downloaded', False),
                'error': context.get('error')
            })

    # render normal
    context.update(sidebar_context)
    return render(request, 'index/download.html', context)
