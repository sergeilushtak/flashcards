from django import forms

class UploadFileForm(forms.Form):
    action_choises = {
        ('overwrite', 'overwrite the vocabulary')
      , ('append', 'append to existing vocabulary')
      , ('add_dates', 'add new dated sections')
    }
#    action = forms.ChoiceField(widget=forms.RadioSelect, choices=action_choises)
    save_file = forms.BooleanField (widget=forms.CheckboxInput, initial=True)

    file = forms.FileField()
