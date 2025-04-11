# forms.py
from django import forms
from db.models import *

class UploadComicForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = ['name', 'artist', 'tags', 'game', 'character']
        def __init__(self, *args, **kwargs):
            super(UploadElementForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['artist'].required = False
            self.fields['artist'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['game'].required = False
            self.fields['game'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['character'].required = False
            self.fields['character'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': ' Personaje', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

            self.fields['tags'].required = False
            self.fields['tags'].widget = forms.CheckboxSelectMultiple()
            self.fields['tags'].queryset = Tags.objects.all()  # Obtén todas las opciones de tags disponibles
        


class UploadElementForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['name', 'artist', 'tags', 'game', 'character', 'file', 'thumbnail']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
        }
    def __init__(self, *args, **kwargs):
        super(UploadElementForm, self).__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['artist'].required = False
        self.fields['artist'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': '', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['game'].required = False
        self.fields['game'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['character'].required = False
        self.fields['character'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': ' Personaje', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})

        self.fields['file'].required = True
        self.fields['file'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2', 'placeholder': ' Archivo*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1','type':'file', 'name':'file', 'accept':'video/*'})

        self.fields['thumbnail'].required = False
        self.fields['thumbnail'].widget.attrs.update({'class': 'rounded-4 border-3 px-4 w-75 py-2 from-control', 'placeholder': ' Miniatura', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1'})
     

        # Asegúrate de que el campo de tags está usando CheckboxSelectMultiple correctamente.
        self.fields['tags'].required = False
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        self.fields['tags'].queryset = Tags.objects.all()  # Obtén todas las opciones de tags disponibles
        

        
class addComentariosForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario','usuario','mediaFile']

    def __init__(self, *args, **kwargs):
        super(addComentariosForm, self).__init__(*args, **kwargs)

        self.fields['comentario'].required = True
        self.fields['comentario'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Introduce tu comentario', 'rows': '1'})

        self.fields['usuario'].required = False
        self.fields['usuario'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': 'Artista*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['mediaFile'].required = False
        self.fields['mediaFile'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})
class addTagsForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = ['name']
    def __init__(self, *args, **kwargs):
            super(addTagsForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce la tag', 'rows': '1'})

class addArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name','image']
    def __init__(self, *args, **kwargs):
            super(addArtistForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce el nombre del artista', 'rows': '1'})

class addCharsForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name','image','game']
    def __init__(self, *args, **kwargs):
            super(addCharsForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce el nombre del personaje', 'rows': '1'})
            self.fields['game'].required = True
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
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(addUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['username'].widget.attrs.update({
            'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2',
            'placeholder': 'Introduce el nombre del usuario',
            'rows': '1'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hashea la contraseña
        if commit:
            user.save()
        return user

class addGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name']
    def __init__(self, *args, **kwargs):
            super(addGameForm, self).__init__(*args, **kwargs)

            self.fields['name'].required = True
            self.fields['name'].widget.attrs.update({'class': 'form-control shadow-none bg-white text-tercero border border-2 border-primary px-2 py-2', 'placeholder': ' Introduce el nombre del juego', 'rows': '1'})
          