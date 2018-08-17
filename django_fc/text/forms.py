from django import forms

class WorkWithTextForm (forms.Form):
    action_choises = {
        ('overwrite', 'overwrite the vocabulary')
      , ('append', 'append existing vocabulary')
      , ('add_dates', 'add new dated sections')
      , ('replace_dates', 'add new and replace existing dated sessions')
    }
    action = forms.ChoiceField(widget=forms.RadioSelect, choices=action_choises)

    save_file = forms.BooleanField (widget=forms.CheckboxInput, initial=True)

    def __init__(self, txt, file_name,  *args, **kwargs):
        super(WorkWithTextForm, self).__init__(*args, **kwargs)

        label = ''
        long_txt_widget = forms.Textarea (
                attrs = {
                    'class' : 'form-control',
                    'rows' : 100,
                    'overflow-y' : 'scroll',
                    'overflow-x' : 'scroll',
                    'ID':'text_area',
                }
        )

        short_txt_widget = forms.TextInput (
                attrs = {
                    'class' : 'form-control',
                }
        )

        self.fields ['file_name'] = forms.CharField (initial = file_name, label = 'File Name', widget = short_txt_widget)
        self.fields ['text'] = forms.CharField (initial = txt, label = label, widget = long_txt_widget)
