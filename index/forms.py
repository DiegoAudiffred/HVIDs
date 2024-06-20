# forms.py
from django import forms
from db.models import MediaFile, Tags

class UploadElementForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['title', 'artist', 'tags', 'game', 'character', 'file', 'thumbnail']

    def __init__(self, *args, **kwargs):
        super(UploadElementForm, self).__init__(*args, **kwargs)

        self.fields['title'].required = True
        self.fields['title'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Nombre que aparece en el menú*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['artist'].required = False
        self.fields['artist'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': 'Artista*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['game'].required = False
        self.fields['game'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Juego', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['character'].required = True
        self.fields['character'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Personaje', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['file'].required = True
        self.fields['file'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Archivo*', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})

        self.fields['thumbnail'].required = False
        self.fields['thumbnail'].widget.attrs.update({'class': 'form-control shadow-none bg-corporateTan200 px-2 py-1', 'placeholder': ' Miniatura', 'rows': '1', 'aria-label': 'Username', 'aria-describedby': 'basic-addon1', 'style': 'border-left:none'})
        self.fields['thumbnail'].initial = 'https://drive.google.com/thumbnail?id='

        # Asegúrate de que el campo de tags está usando CheckboxSelectMultiple correctamente.
        self.fields['tags'].required = False
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        self.fields['tags'].queryset = Tags.objects.all()  # Obtén todas las opciones de tags disponibles
