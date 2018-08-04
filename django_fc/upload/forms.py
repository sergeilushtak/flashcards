from django import forms

class UploadFileForm(forms.Form):
    aggregate_choises = {
        ('overwrite', 'overwrite')
      , ('append', 'append')
      , ('append_dates', 'append dates')
    }
    aggregate = forms.ChoiceField(widget=forms.RadioSelect, choices=aggregate_choises)

    file = forms.FileField()
