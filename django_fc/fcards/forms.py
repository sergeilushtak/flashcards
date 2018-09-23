from django import forms

class EditVocEntryForm (forms.Form):

    def __init__(self, vdbe, *args, **kwargs):
        super(EditVocEntryForm, self).__init__(*args, **kwargs)
        # dynamic fields here ...

        short_txt_widget = forms.TextInput (
                attrs = {
                    'class' : 'form-control',
                }
        )
        long_txt_widget = forms.Textarea (
                attrs = {
                    'class' : 'form-control',
                    'rows' : 2,
                }
        )

        self.fields ['lemma_ID'] = forms.CharField (initial=vdbe.lemma_ID, widget=short_txt_widget)
        self.fields ['lft_lemma_ID'] = forms.CharField (initial=vdbe.lft_lemma_ID, widget=short_txt_widget)
        self.fields ['lft_usage_ID'] = forms.CharField (initial=vdbe.lft_usage_ID, widget=short_txt_widget)

        self.fields ['rgt_lemma_ID'] = forms.CharField (initial=vdbe.rgt_lemma_ID, widget=short_txt_widget)
        self.fields ['rgt_usage_ID'] = forms.CharField (initial=vdbe.rgt_usage_ID, widget=short_txt_widget)

        self.fields ['lft_lemma_display'] = forms.CharField (initial=vdbe.lft_lemma_display, widget=short_txt_widget)
        self.fields ['rgt_lemma_display'] = forms.CharField (initial=vdbe.rgt_lemma_display, widget=short_txt_widget)

        citL = vdbe.get_citL ()
        ctxL = vdbe.get_ctxL ()


        self.fields ['ctx 0'] = forms.CharField(initial= ctxL [0], label = 'Context', widget=long_txt_widget)

        for ii in range (len (citL)):
            self.fields ['cit ' + str (ii) ] = forms.CharField (initial=citL [ii], label = 'Citation', widget=short_txt_widget)
            self.fields ['ctx ' + str (ii + 1) ] = forms.CharField (initial = ctxL [ii + 1], label = 'Context', widget=long_txt_widget)


    # normal fields here ...

    def to_vdbe (self, vdbe):

        data = self. cleaned_data
        print (data)
        vdbe.rgt_lemma_ID = data ['rgt_lemma_ID']
        vdbe.rgt_lemma_display = data ['rgt_lemma_display']
        vdbe.rgt_usage_ID = data ['rgt_usage_ID']

        vdbe.lft_lemma_ID = data ['lft_lemma_ID']
        vdbe.lft_lemma_display = data ['lft_lemma_display']
        vdbe.lft_usage_ID = data ['lft_usage_ID']

        vdbe.lemma_ID = data['lemma_ID']
    #    vdbe.correct_answer = data ['correct_answer']

        citL = []
        ctxL = []
        for field, value in data.items ():
            spl = field.split (' ')
            if len (spl) == 2 and spl [1].isdigit ():
                ind = int (spl [1])
                if spl [0] == 'cit':
                    citL.append ((ind, value))
                else:
                    ctxL.append ((ind, value))

        citL.sort ()
        ctxL.sort ()

        citL = [item [1] for  item in citL]
        ctxL = [item [1] for item in ctxL]
        vdbe.cits = '|'.join (citL)
        vdbe.ctxs = '|'.join (ctxL)
        print (vdbe.cits)
        print (vdbe.ctxs)
