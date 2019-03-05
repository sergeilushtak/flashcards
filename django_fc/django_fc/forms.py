from django import forms

class SettingsForm (forms.Form):

    def __init__(self, stt, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

        self.fields ['mode'] = forms.CharField (initial = stt.session.mode, label = 'Mode')
        self.fields ['frequency'] = forms.IntegerField (initial = stt.voc.frequency, label = 'Sample only as or more frequent. Frequency')
        self.fields ['chunk_size'] = forms.IntegerField (initial = stt.chunk.size, label = 'Maximum chunk size')
        self.fields ['punitive_rhn'] = forms.IntegerField (initial = stt.session.rhn_punitive, label = 'Punitive required hit number')
        self.fields ['initial_rhn'] = forms.IntegerField (initial = stt.session.rhn_initial, label = 'Initial required hit number')

        self.fields ['fw_lesson_size'] = forms.IntegerField (initial = stt.lessons.lesson, label = 'Floating window lesson size')
        self.fields ['fw_review_lesson_cnt'] = forms.IntegerField (initial = stt.lessons.window, label = 'Floating window: review lesson count')


    def to_stt (self, stt):
        data = self.cleaned_data

        stt.session.mode = data ['mode']
        stt.voc.frequency = data ['frequency']
        stt.chunk.size = data ['chunk_size']
        stt.session.rhn_punitive = data ['punitive_rhn']
        stt.session.rhn_initial = data ['initial_rhn']

        stt.lessons.lesson = data ['fw_lesson_size']
        stt.lessons.window = data ['fw_review_lesson_cnt']

from fcards.models import Project
from fcards.models import Language

class NewProjectForm (forms.Form):


    def __init__ (self, *args, **kwargs):
        super(NewProjectForm, self).__init__(*args, **kwargs)

        lang_obj_L = Language.objects.all ()
        lang_choiceL = []
        for lang_obj in lang_obj_L:
            lang_choiceL.append ((lang_obj.name, lang_obj.name))

        self.fields ['name'] = forms.CharField ()
        self.fields ['language'] = forms.CharField (
            label='Chose Project Language',
            widget=forms.Select (choices=lang_choiceL)
            )
        self.fields ['allow_sharing'] = forms.BooleanField (widget=forms.CheckboxInput, initial=True)
