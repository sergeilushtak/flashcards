from django import forms

class SettingsForm (forms.Form):

    def __init__(self, stt, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

        self.fields ['mode'] = forms.CharField (initial = stt.session.mode, label = 'Mode')
        self.fields ['frequency'] = forms.IntegerField (initial = stt.voc.frequency, label = 'Sample only as or more frequent. Frequency')
#        self.fields ['chunk_size'] = forms.IntegerField (initial = stt.chunk.size, label = 'Maximum chunk size')
        self.fields ['punitive_rhn'] = forms.IntegerField (initial = stt.session.rhn_punitive, label = 'Punitive required hit number')
        self.fields ['initial_rhn'] = forms.IntegerField (initial = stt.session.rhn_initial, label = 'Initial required hit number')
        self.fields ['extract_sentences'] = forms.BooleanField (
            widget=forms.CheckboxInput,
            initial = stt.extract_sentences,
            label = 'Break up input text into sentences',
            required = False
        )
        self.fields ['randomize'] = forms.BooleanField (
            widget=forms.CheckboxInput,
            initial = stt.session.randomize,
            label = 'Randomize session',
            required = False
        )

        self.fields ['fw_lesson_size'] = forms.IntegerField (initial = stt.lessons.lesson, label = 'Sliding window: lesson size')
        self.fields ['fw_review_lesson_cnt'] = forms.IntegerField (initial = stt.lessons.window, label = 'Sliding window: \"Review Session\" lesson count')
        self.fields ['lessons_rand_old'] = forms.IntegerField (initial = stt.lessons.rand_old, label = 'Maximum \"Random Older Entries\" session size')

    def to_stt (self, stt):
        data = self.cleaned_data

        stt.extract_sentences = data ['extract_sentences']

        stt.session.mode = data ['mode']
        stt.voc.frequency = data ['frequency']
#        stt.chunk.size = data ['chunk_size']
        stt.session.rhn_punitive = data ['punitive_rhn']
        stt.session.rhn_initial = data ['initial_rhn']
        stt.session.randomize = data ['randomize']

        stt.lessons.lesson = data ['fw_lesson_size']
        stt.lessons.window = data ['fw_review_lesson_cnt']
        stt.lessons.rand_old = data ['lessons_rand_old']

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
        self.fields ['allow_sharing'] = forms.BooleanField (
            widget=forms.CheckboxInput,
            initial=True,
            required = False,
            )


class EditProjectForm (forms.Form):


    def __init__ (self, cur_proj, *args, **kwargs):
        super (EditProjectForm, self).__init__(*args, **kwargs)

        lang_obj_L = Language.objects.all ()
        lang_choiceL = []
        for lang_obj in lang_obj_L:
            lang_choiceL.append ((lang_obj.name, lang_obj.name))

        self.fields ['name'] = forms.CharField (initial = cur_proj.name)

        self.fields ['language'] = forms.CharField (
            label='Chose Project Language',
            widget=forms.Select (choices=lang_choiceL),
            initial = cur_proj.language,
            )
        self.fields ['allow_sharing'] = forms.BooleanField (
          widget=forms.CheckboxInput,
          initial= not cur_proj.secret,
          required = False,
        )
