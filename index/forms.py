# forms.py
from django import forms
from db.models import *


class UploadComicForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = ['name', 'artist', 'tags', 'game', 'character', 'user', 'hide', 'image', 'nsfw']

    def __init__(self, *args, **kwargs):
        super(UploadComicForm, self).__init__(*args, **kwargs)
        checkbox_style = {'class': 'form-check-input fs-2 my-0'}
        input_style = {'class': 'rounded-4 border-3 px-4 w-100 py-2'}

        self.fields['name'].widget.attrs.update(input_style)
        self.fields['artist'].widget.attrs.update(input_style)
        self.fields['game'].widget.attrs.update(input_style)
        self.fields['user'].widget.attrs.update(input_style)
        
        self.fields['hide'].widget.attrs.update(checkbox_style)
        self.fields['nsfw'].widget.attrs.update(checkbox_style)

        self.fields['character'].required = False
        self.fields['character'].widget = forms.CheckboxSelectMultiple()
        
        if self.data.get('comic-game'):
            try:
                game_id = int(self.data.get('comic-game'))
                self.fields['character'].queryset = Character.objects.filter(game_id=game_id)
            except (ValueError, TypeError):
                self.fields['character'].queryset = Character.objects.none()
        else:
            self.fields['character'].queryset = Character.objects.none()

        self.fields['tags'].required = False
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        self.fields['tags'].queryset = Tags.objects.all()


class uploadFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['name', 'artist', 'tags', 'game', 'character', 'file', 'image', 'hide', 'user', 'nsfw']

    def __init__(self, *args, **kwargs):
        super(uploadFileForm, self).__init__(*args, **kwargs)
        control_style = 'form-control rounded-3 border-secondary-subtle shadow-sm px-3 py-2'
        select_style = 'form-select rounded-3 border-secondary-subtle shadow-sm px-3 py-2'
        check_style = 'form-check-input'

        self.fields['name'].widget.attrs.update({'class': control_style, 'placeholder': 'Ej. Mi Video Increíble'})
        self.fields['artist'].widget.attrs.update({'class': select_style})
        self.fields['game'].widget.attrs.update({'class': select_style})
        self.fields['file'].widget.attrs.update({'class': control_style, 'accept': 'video/*'})
        self.fields['image'].widget.attrs.update({'class': control_style})
        
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['hide'].widget.attrs.update({'class': check_style})
        self.fields['nsfw'].widget.attrs.update({'class': check_style})

        self.fields['character'].required = False
        self.fields['character'].widget = forms.CheckboxSelectMultiple()
        
        if self.data.get('video-game'):
            try:
                game_id = int(self.data.get('video-game'))
                self.fields['character'].queryset = Character.objects.filter(game_id=game_id)
            except (ValueError, TypeError):
                self.fields['character'].queryset = Character.objects.none()
        else:
            self.fields['character'].queryset = Character.objects.none()

        self.fields['tags'].required = False
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        self.fields['tags'].queryset = Tags.objects.all()
class ComicPageForm(forms.ModelForm):
    class Meta:
        model = ComicPage
        fields = ['image', 'order']

class addComentariosForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario','usuario','mediaFileID',]

    def __init__(self, *args, **kwargs):
        super(addComentariosForm, self).__init__(*args, **kwargs)

        self.fields['comentario'].required = True
        self.fields['comentario'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Introduce tu comentario', 'rows': '1'})

        self.fields['usuario'].required = False
        self.fields['usuario'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': 'Artista*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['mediaFileID'].required = False
        self.fields['mediaFileID'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})
class addTagsForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = ['name']
    def __init__(self, *args, **kwargs):
            super(addTagsForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce la tag', 'rows': '1'})


class addArtistForm(forms.ModelForm):
    # campos virtuales para redes
    facebook  = forms.CharField(required=False, label="Facebook", max_length=255)
    twitter   = forms.CharField(required=False, label="Twitter", max_length=255)
    instagram = forms.CharField(required=False, label="Instagram", max_length=255)
    youtube   = forms.CharField(required=False, label="YouTube", max_length=255)
    tiktok    = forms.CharField(required=False, label="TikTok", max_length=255)
    onlyfans  = forms.CharField(required=False, label="OnlyFans", max_length=255)
    rule34    = forms.CharField(required=False, label="Rule34", max_length=255)
    patreon    = forms.CharField(required=False, label="Patreon", max_length=255)
    coomer_kemono    = forms.CharField(required=False, label="Coomer_Kemono ", max_length=255)

    # 🔵 Aquí defines birthdate manualmente:
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',            # <-- ISO para <input type="date">
            attrs={
                'type': 'date',           # activa el calendario nativo
                'class': 'form-control …',
                'placeholder': 'dd/mm/aaaa',
            }
        )
    )

    class Meta:
        model = Artist
        fields = [
            'name', 'image', 'gender', 'tags', 'description', 'birthdate',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows':4,'class':'form-control'}),
            'name':        forms.TextInput(attrs={'class':'form-control form-control-lg'}),
            'gender':      forms.RadioSelect(choices=[(True,'Masculino'),(False,'Femenino')]),
            # tags oculto para usar tu tag-picker
            # birthdate ya no lo defines aquí, porque ya lo definimos arriba
        }

    def clean(self):
        cleaned = super().clean()
        social = {}
        for key in ['facebook','twitter','instagram','youtube','tiktok','onlyfans','rule34','patreon','coomer_kemono']:
            val = cleaned.get(key)
            if val:
                social[key] = val
        cleaned['social_media'] = social
        return cleaned

    def save(self, commit=True):
        self.instance.social_media = self.cleaned_data['social_media']
        return super().save(commit=commit)

    def __init__(self, *args, **kwargs):
        super(addArtistForm, self).__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 
            'placeholder': ' Introduce el nombre del artista', 
            'rows': '1'
        })

        self.fields['description'].required = False
        self.fields['description'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': ' Añade una breve descripción',
            'rows':'4'
        })

        self.fields['tags'].required = False
        self.fields['tags'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': ' Introduce los tags del artista',
            'rows': '1'
        })

        # 🔵 birthdate ya tiene su widget correcto arriba

        # inicializar los valores desde el JSON existente
        social = self.instance.social_media or {}
        for field in ['facebook','twitter','instagram','youtube','tiktok','onlyfans','rule34','patreon','coomer_kemono']:
            self.fields[field].initial = social.get(field,'')

        # aplica clase bootstrap a los virtuales
        for field in ['facebook','twitter','instagram','youtube','tiktok','onlyfans','rule34','patreon','coomer_kemono']:
            self.fields[field].widget.attrs.setdefault('class','form-control')


class addCharsForm(forms.ModelForm):
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',            # <-- ISO para <input type="date">
            attrs={
                'type': 'date',           # activa el calendario nativo
                'class': 'form-control …',
                'placeholder': 'dd/mm/aaaa',
            }
        )
    )

    class Meta:
        model = Character
        fields = ['name','image','game','description','gender','birthdate','tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4,'class':'form-control'}),
            'name':        forms.TextInput(attrs={'class':'form-control form-control-lg'}),
            'gender':      forms.RadioSelect(choices=[(True,'Masculino'),(False,'Femenino')]),
            # tags oculto para usar tu tag-picker
            # birthdate ya no lo defines aquí, porque ya lo definimos arriba
        }
    def __init__(self, *args, **kwargs):
            super(addCharsForm, self).__init__(*args, **kwargs)
            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 
            'placeholder': ' Introduce el nombre del personaje', 
            'rows': '1'
        })

            self.fields['description'].required = False
            self.fields['description'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': ' Añade una breve descripción',
            'rows':'4'
        })

            self.fields['tags'].required = False
            self.fields['tags'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': ' Introduce los tags del personaje',
            'rows': '1'
        })

            
            self.fields['game'].required = False
            self.fields['game'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce el nombre del personaje', 'rows': '1'})
    
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class addUserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': 'Introduce una contraseña',
        }),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'is_staff', 'is_superuser','image','banner']

    def __init__(self, *args, **kwargs):
        super(addUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].required = True
        self.fields['username'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': 'Introduce el nombre del usuario',
            'rows': '1'
        })

        # Estilos personalizados para las checkboxes
        checkbox_style = {
            'class': 'form-check-input fs-3 mx-2 my-0',  # Tamaño más grande con Bootstrap 5
            'style': 'transform: scale(1.5);'        # Agranda aún más la checkbox
        }

        self.fields['is_staff'].widget.attrs.update(checkbox_style)
        self.fields['is_superuser'].widget.attrs.update(checkbox_style)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hashea la contraseña
        if commit:
            user.save()
        return user



class editUserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': 'Introduce una contraseña nueva (opcional)',
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'image', 'banner']  # ← ¡Ojo! No incluimos 'password'

    def __init__(self, *args, **kwargs):
        super(editUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['username'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2 my-2',
            'placeholder': 'Introduce el nombre del usuario',
            'rows': '1'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        else:
            # Preserva el hash de contraseña actual si no se cambia
            user.password = self.instance.password

        if commit:
            user.save()
        return user

 


class addGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name','image','tags']
    def __init__(self, *args, **kwargs):
            super(addGameForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce el nombre del juego', 'rows': '1'})
            
            self.fields['tags'].required = False
            self.fields['tags'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2 my-2',
            'placeholder': ' Introduce los tags del personaje',
            'rows': '1'
        })


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe tu post'}),
          
        }
    def __init__(self, *args, **kwargs):
            super(PostForm, self).__init__(*args, **kwargs)

            self.fields['name'].widget.attrs.update({
    'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
    'placeholder': 'Introduce el nombre de la nota'
})

            self.fields['description'].widget.attrs.update({
    'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
    'placeholder': 'Descripción del post'
})
            

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe tu post'}),
          
        }
    def __init__(self, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': 'Descripción del post',
            'maxlength': '500'  
        })

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) > 500:
            raise forms.ValidationError("La descripción no puede tener más de 500 caracteres.")
        return description
