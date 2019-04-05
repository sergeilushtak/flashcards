from django import forms

class WorkWithTextForm (forms.Form):
    action_choises = {
        ('overwrite', 'overwrite the vocabulary')
      , ('append', 'append to existing vocabulary')
      , ('add_dates', 'add new dated sections')
    }
    #action = forms.ChoiceField(widget=forms.RadioSelect, choices=action_choises, initial='add_dates')

    save_file = forms.BooleanField (
        widget=forms.CheckboxInput,
        initial=True,
        label="Save file upon \"Submit Citations\"",
        required = False,

        )

    def __init__(self, txt, file_name,  *args, **kwargs):
        super(WorkWithTextForm, self).__init__(*args, **kwargs)

        label = ''
        long_txt_widget = forms.Textarea (
                attrs = {
                    'class' : 'form-control',
                    'rows' : 25,
                    'overflow-y' : 'scroll',
                    'overflow-x' : 'scroll',
                    'ID':'text_area',
                }
        )

        file_name_widget = forms.TextInput (
                attrs = {
                    'class' : 'form-control',
                    'ID':'file_name_box'
                }
        )

        self.fields ['file_name'] = forms.CharField (initial = file_name, label = 'File Name', widget = file_name_widget)
        self.fields ['text'] = forms.CharField (initial = txt, label = label, widget = long_txt_widget)



class GenerateSourceForm (forms.Form):

    def __init__(self, txt,  *args, **kwargs):
        super(GenerateSourceForm, self).__init__(*args, **kwargs)

        label = ''
        long_txt_widget = forms.Textarea (
                attrs = {
                    'class' : 'form-control',
                    'rows' : 25,
                    'overflow-y' : 'scroll',
                    'overflow-x' : 'scroll',
                    'ID':'text_area',
                }
        )

        file_name_widget = forms.TextInput (
                attrs = {
                    'class' : 'form-control',
                    'ID':'file_name_box'
                }
        )

        self.fields ['file_name'] = forms.CharField (label = 'File Name', widget = file_name_widget)
        self.fields ['text'] = forms.CharField (initial = txt, label = label, widget = long_txt_widget)
