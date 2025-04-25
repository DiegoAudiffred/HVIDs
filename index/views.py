import datetime

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

from django.shortcuts import redirect

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

                # ❌ No repitas formArtist.save()
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
@login_required(login_url='/login/')  

def watchContent(request, id):
    mediafile = get_object_or_404(MediaFile, id=id)

    if request.method == 'POST':
        form = addComentariosForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            
            comentario.usuario = request.user 
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

@login_required(login_url='/login/')  # ruta de la vista login
def detailsAbout(request, filtro, valor):
    sidebar_context = get_sidebar_context()
    if filtro == "personaje":
        resultado = Character.objects.get(name=valor)
        media_files = MediaFile.objects.filter(character=resultado)
        comics = Comic.objects.filter(character=resultado)

        combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True)
        context = {
            'contenido':combined_media,
            'resultado': resultado,
            'filtro': filtro,
            'valor': valor,
            **sidebar_context,
        }
        
    elif filtro=="artista":
        resultado = Artist.objects.get(name=valor)
        media_files = MediaFile.objects.filter(artist=resultado)
        comics = Comic.objects.filter(artist=resultado)

        combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True)
       
        context = {
            'contenido':combined_media,
            'resultado': resultado,
            'filtro': filtro,
            'valor': valor,
            **sidebar_context,
        }
    elif filtro=="juego":
        resultado = Game.objects.get(name=valor)
        media_files = MediaFile.objects.filter(game=resultado)
        comics = Comic.objects.filter(game=resultado)

        combined_media = sorted(
        chain(media_files, comics),
        key=lambda x: x.uploaded_at,
        reverse=True)[:6]
       
        context = {
            'contenido':combined_media,
            'resultado': resultado,
            'filtro': filtro,
            'valor': valor,
            **sidebar_context,
        }
    else:
        context = {
            'mensaje': "Filtro no reconocido",
            **sidebar_context,
        }

    return render(request, 'index/filteredInfoPage.html', context)

@require_POST
def ajax_add_comment(request, id):
    form = addComentariosForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.usuario = request.user
        comentario.mediaFileID_id = id
        comentario.save()
        return JsonResponse({
            'usuario': str(comentario.usuario),
            'fecha': comentario.uploaded_at.strftime('%d/%m/%Y %H:%M'),
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

                # renombrado de archivo
                uploaded_file = request.FILES['file']
                base_name, ext = os.path.splitext(uploaded_file.name)
                upload_dir = datetime.datetime.now().strftime("media_files/%Y%m%d/")
                final_name = f"{base_name}{ext}"
                count = 1
                while default_storage.exists(os.path.join(upload_dir, final_name)):
                    final_name = f"{base_name}_{count}{ext}"
                    count += 1
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
    context = {}
    modelo_map = {
        'personaje': (Character, CharacterFormEdit),
        'artista': (Artist, ArtistFormEdit),
        'juego': (Game, GameFormEdit),
    }
    if tipo not in modelo_map:
        return redirect('index:index')  # o lanza error

    modelo, formulario_clase = modelo_map[tipo]
    instancia = get_object_or_404(modelo, pk=pk)
    print(instancia)
    if request.method == 'POST':
        form = formulario_clase(request.POST, request.FILES, instance=instancia)
        print(tipo,instancia)

        if form.is_valid():
            form.save()
            return redirect('index:detailsAbout', filtro=tipo, valor=instancia.name)
    else:
        form = formulario_clase(instance=instancia)
    sidebar_context = get_sidebar_context()
    context = {
        'form': form,
        'tipo': tipo,
        'instancia':instancia,
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
