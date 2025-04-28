# forms.py
from django import forms
from db.models import *


    

class UploadComicForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = ['name', 'artist', 'tags', 'game', 'character','user','hide','image']
    def __init__(self, *args, **kwargs):
            super(UploadComicForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})
 # Estilos personalizados para las checkboxes
            checkbox_style = {
    'class': 'form-check-input fs-2 my-0',  # Tamaño más grande + margen derecho y vertical
}
            self.fields['hide'].widget.attrs.update(checkbox_style)


            self.fields['artist'].required = False
            self.fields['artist'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['game'].required = False
            self.fields['game'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['character'].required = False
            self.fields['character'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': ' Personaje', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['tags'].required = False
            self.fields['tags'].widget = forms.CheckboxSelectMultiple()
            self.fields['tags'].queryset = Tags.objects.all()  # Obtén todas las opciones de tags disponibles
        
class ComicPageForm(forms.ModelForm):
    class Meta:
        model = ComicPage
        fields = ['image', 'order']

class UploadElementForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
    queryset=Tags.objects.all(),
    required=False,
    widget=forms.SelectMultiple(attrs={
            'class': 'form-control d-none',  # ocultamos el select
            'id': 'id_tags_real'
        })
    )
    class Meta:
        model = MediaFile
        fields = ['name', 'artist', 'tags', 'game', 'character', 'file', 'image','hide']
        
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
        }
    def __init__(self, *args, **kwargs):
        super(UploadElementForm, self).__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['artist'].required = False
        self.fields['artist'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['game'].required = False
        self.fields['game'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['character'].required = False
        self.fields['character'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': ' Personaje', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['file'].required = True
        self.fields['file'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2', 'placeholder': ' Archivo*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1','type':'file', 'name':'file', 'accept':'video/*'})

        self.fields['image'].required = False
        self.fields['image'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-100 py-2 from-control', 'placeholder': ' Miniatura', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})
      # Estilos personalizados para las checkboxes
        checkbox_style = {
    'class': 'form-check-input fs-2 my-0',  # Tamaño más grande + margen derecho y vertical
}
        self.fields['hide'].widget.attrs.update(checkbox_style)

        # Asegúrate de que el campo de tags está usando CheckboxSelectMultiple correctamente.
        self.fields['tags'].required = False
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        self.fields['tags'].queryset = Tags.objects.all()  # Obtén todas las opciones de tags disponibles
        

        
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
    extra1    = forms.CharField(required=False, label="Red extra 1", max_length=255)
    extra2    = forms.CharField(required=False, label="Red extra 2", max_length=255)
    extra3    = forms.CharField(required=False, label="Red extra 3", max_length=255)

    # 🔵 Aquí defines birthdate manualmente:
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%d/%m/%Y', 
            attrs={
                'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
                }
        ),
        input_formats=['%d/%m/%Y'],
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
        for key in ['facebook','twitter','instagram','youtube','tiktok','onlyfans','extra1','extra2','extra3']:
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
        for field in ['facebook','twitter','instagram','youtube','tiktok','onlyfans','extra1','extra2','extra3']:
            self.fields[field].initial = social.get(field,'')

        # aplica clase bootstrap a los virtuales
        for field in ['facebook','twitter','instagram','youtube','tiktok','onlyfans','extra1','extra2','extra3']:
            self.fields[field].widget.attrs.setdefault('class','form-control')


class addCharsForm(forms.ModelForm):
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%d/%m/%Y', 
            attrs={
                'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
                'placeholder': 'dd/mm/yyyy'
            }
        ),
        input_formats=['%d/%m/%Y'],
    )
    class Meta:
        model = Character
        fields = ['name','image','game','description','gender','birthdate']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4,'class':'form-control'}),
            'name':        forms.TextInput(attrs={'class':'form-control form-control-lg'}),
            'gender':      forms.RadioSelect(choices=[(True,'Masculino'),(False,'Femenino')]),
            # tags oculto para usar tu tag-picker
            # birthdate ya no lo defines aquí, porque ya lo definimos arriba
        }
    def __init__(self, *args, **kwargs):
            super(addCharsForm, self).__init__(*args, **kwargs)
    
            
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
        fields = ['username', 'password', 'is_staff', 'is_superuser']

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

class addGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name','image','tags']
    def __init__(self, *args, **kwargs):
            super(addGameForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce el nombre del juego', 'rows': '1'})
         