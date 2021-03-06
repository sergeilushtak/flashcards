from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse

from . import models
from .models import FCSettings
from .models import ProcessedInPast

from fc_engine.back_end import session
from fc_engine.settings import Settings

from django.contrib.auth import get_user_model
User = get_user_model()





def roll_back (request):

    ss = session ()
    ss.from_json (request.session ['ss'])
    ss.roll_back ()
    request.session ['ss'] = ss.to_json ()

    return HttpResponseRedirect(reverse('fcards:user_guessing'))

def roll_forward (request):

    ss = session ()
    ss.from_json (request.session ['ss'])
    ss.roll_forward ()
    request.session ['ss'] = ss.to_json ()

    return HttpResponseRedirect(reverse('fcards:user_guessing'))

def start_session_randold (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    project_id = request.session ['project_id']
    all_voc = models.all_to_dbvoc (request.user.id, project_id)

    idL = all_voc.get_dated_idL_given_date_ind ((0, -2))

    ss = session ()
    """
    print ('mydebug>>>> start_session_randold : calling ss.start')
    print ()
    print (idL)
    print ()
    """
    if ss.start (stt, all_voc, idL, stt.lessons.rand_old):

        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))


def start_session_all (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    project_id = request.session ['project_id']
    all_voc = models.all_to_dbvoc (request.user.id, project_id)

    idL = all_voc.get_idL ()

    ss = session ()
    if ss.start (stt, all_voc, idL):

        #eng = engine ()
        #eng.start ()

        #request.session ['eng']     =  eng.to_json ()

        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()



        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))

def start_session_dated (request, *args, **kwargs):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    #index = int (kwargs ['index']) - 1

    date  = kwargs  ['date']

    project_id = request.session ['project_id']
    all_voc = models.all_to_dbvoc (request.user.id, project_id)
#    idL = all_voc.get_dated_idL (index)
    idL = all_voc.get_dated_idL (date)

    ss = session ()
    if ss.start (stt, all_voc, idL):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))


def start_session_intervalled (request, *args, **kwargs):

    stt = Settings ()
    #print (request.session ['stt'])
    stt.from_json (request.session ['stt'])
    #print ("start_session_intervalled:::: stt.randomize = {}".format (stt.session.randomize))

    #index = int (kwargs ['index']) - 1

    start  = int (kwargs  ['start'])
    size = int (kwargs ['size'])

    project_id = request.session ['project_id']
    all_voc = models.all_to_dbvoc (request.user.id, project_id)
#    idL = all_voc.get_dated_idL (index)

    idL = all_voc.get_intervalled_idL (start, size)

    ss = session ()
    if ss.start (stt, all_voc, idL):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))


def start_session_intervalled_random (request, *args, **kwargs):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    #index = int (kwargs ['index']) - 1

    start  = int (kwargs  ['start'])
    size = int (kwargs ['size'])

    project_id = request.session ['project_id']
    all_voc = models.all_to_dbvoc (request.user.id, project_id)
#    idL = all_voc.get_dated_idL (index)

    idL = all_voc.get_intervalled_idL (start, size)

    ss = session ()
    if ss.start (stt, all_voc, idL, stt.lessons.rand_old):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))



def end_of_session (request):


    ss = session ()
    ss.from_json (request.session ['ss'])
    ss.end ()


    stats = dict ()

    stats ['kills'] = "Total words processed: {}".format (ss.stats.kills)
    stats ['clean_kills'] = "First try guesses: {}".format (ss.stats.clean_kills)
    if ss.stats.alive == 0 and ss.stats.kills == ss.stats.clean_kills:
        stats ['congrats'] = "*** Congrats!!! ***"
    elif ss.stats.alive > 0:
        stats ['yet_to_process'] = "Total words yet to process: {}".format (ss.stats.alive)
        stats ['yet_untouched'] = "Total words yet untouched: {}".format (ss.stats.untouched)

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    if stt.session.mode == 'generation':
        other_fc_mode = 'recognition'
    else:
        other_fc_mode = 'generation'

    stats ['other_fc_mode'] = other_fc_mode

    request.session ['ss'] = ss.to_json ()

    return render(request, 'end_of_session.html', context=stats)



def restart_session_in_other_mode (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    if stt.session.mode == 'generation':
        stt.session.mode = 'recognition'
    else:
        stt.session.mode = 'generation'
    request.session ['stt'] = stt.to_json ()

    project_id = request.session ['project_id']

    dbst = FCSettings.objects.filter (user_id=request.user.id).get(project_id=project_id)
    dbst.from_stt (stt)
    dbst.save ()


    ss = session ()
    ss.from_json (request.session ['ss'])
    ss.restart ()
    request.session ['ss'] = ss.to_json ()

    return HttpResponseRedirect(reverse('fcards:user_guessing'))




def end_session_done (request):

    ss = session ()
    ss.from_json (request.session ['ss'])

    idS = ss.register_dead ()

    project_id = request.session ['project_id']
    user_id = request.user.id

    for id in idS:

        # find entry (ID)
        vdbe = get_vdbe (id)
        lemma_ID = vdbe.lft_lemma_ID + '__' + vdbe.rgt_lemma_ID

        try :
            #dbst = FCSettings.objects.filter (user_id=request.user.id).get(project_id=project_id)
            pip = ProcessedInPast.objects.filter (user_id=request.user.id, project_id=project_id).get (lemma_ID=lemma_ID)

#            pip = ooo.get (lemma_ID=lemma_ID)
            pip.times_processed += 1
            print ("========= pip don't exist ================")

        except models.ProcessedInPast.DoesNotExist:
            pip = ProcessedInPast ()
            pip.user_id = user_id
            pip.project_id = project_id
            pip.lemma_ID = lemma_ID
            pip.times_processed = 1

        print ("............. Saving Pip (((((((((((())))))))))))")
        pip.save ()

    return HttpResponseRedirect(reverse('home'))


def resume_session (request):

    ss = session ()
    ss.from_json (request.session ['ss'])
    ss.resume ()
    request.session ['ss'] = ss.to_json ()

    return HttpResponseRedirect(reverse('fcards:user_guessing'))

def funnel (request):

    ss = session ()
    ss.from_json (request.session ['ss'])
    ss.funnel ()
    request.session ['ss'] = ss.to_json ()

    return HttpResponseRedirect(reverse('fcards:user_guessing'))



from  . import forms
from .models import VocEntry, get_vdbe, Project

def edit_btn_on_click (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    ss = session ()
    ss.from_json (request.session ['ss'])
    project_id = request.session ['project_id']
    project_obj = Project.objects.filter (user_id=request.user.id).get (id=project_id)
    language_id = project_obj.language_id

    #all_voc = dbVoc ()
    #all_voc.from_json (request.session ['all_voc'])

    #vdbe = all_voc.get_voc_entry (str (ss.get_cur_entry_ID ()))
    vdbe = get_vdbe (ss.get_cur_entry_ID ())

    form = forms.EditVocEntryForm (vdbe)

    if request.method == 'POST':
        form = forms.EditVocEntryForm (vdbe, request.POST)
        if form.is_valid ():
            form.to_vdbe (vdbe)
            ve = models.VocEntry ()
            ve.from_vdbe (vdbe)
            ve.id = vdbe.ID
            ve.user_id = request.user.id
            ve.project_id = project_id
            ve.language_id = language_id

    #        request.session ['all_voc'] =  all_voc.to_json ()

            ve.save ()
            return  HttpResponseRedirect (reverse ("fcards:awaiting_approval"))

    return render (request, 'edit_entry.html', {'form':form})




class UserGuessing (TemplateView):
    template_name = 'user_guessing.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self,**kwargs):
        context  = super().get_context_data(**kwargs)

        stt = Settings ()
        stt.from_json (self.request.session ['stt'])

        #all_voc = dbVoc ()
        #all_voc.from_json (self.request.session ['all_voc'])
        ss = session ()
        ss.from_json (self.request.session ['ss'])

        #print ("mydebug >>> views.UserGuessing eng.running : {}".format (eng.running))

        #vdbe = all_voc.get_voc_entry (str (ss.get_cur_entry_ID()))
        vdbe = get_vdbe (ss.get_cur_entry_ID ())
        #print ("mydebug >>> views.UserGuessing cur_entry_ind = {}".format (ss.chunk.cur_entry_ind))
        #print ("mydebug >>> views.UserGuessing cur_entry_ID = {}".format (ss.get_cur_entry_ID()))

        if stt.session.mode == 'generation':
            context ['question'] = vdbe.rgt_lemma_display
#            context ['context'] = vdbe.get_rgt_ctx_str ()
            citL = vdbe.get_citL ()
            ctxL = vdbe.get_ctxL ()
            str_out = ctxL [0]

            for ii in range (len (citL)):
                cit_spl = [w.strip () for w in citL[ii].split ('=')]

                str_out += '<span class=active_cit>' + cit_spl [1] + '</span>'
                str_out += ctxL [ii + 1]
    #        context ['question'] += '<br>' + str_out
            context ['context'] = str_out

        else:
            context ['question'] = vdbe.lft_lemma_display

        context ['question'] = '<span class=lemma>' +  context ['question'] + '</span>'

        context['session_size'] = len (ss)
        context['rhn'] = ss.get_cur_entry_rhn ()


        return context


class AwaitingApproval (TemplateView):
    template_name = 'awaiting_approval.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    def get_context_data(self,**kwargs):

        stt = Settings ()
        stt.from_json (self.request.session ['stt'])

        context  = super().get_context_data(**kwargs)

        #all_voc = dbVoc ()
        #all_voc.from_json (self.request.session ['all_voc'])
        ss = session ()
        ss.from_json (self.request.session ['ss'])

        #vdbe = all_voc.get_voc_entry (str (ss.get_cur_entry_ID()))
        vdbe = get_vdbe (ss.get_cur_entry_ID())

        if stt.session.mode == 'generation':
            context ['answer'] = vdbe.rgt_lemma_display + ' = ' + vdbe.lft_lemma_display
#            context ['context'] = vdbe.get_lft_ctx_str ()
            citL = vdbe.get_citL ()
            ctxL = vdbe.get_ctxL ()
            str_out = ctxL [0]

            for ii in range (len (citL)):
                cit_spl = [w.strip () for w in citL[ii].split ('=')]
                str_out += '<span class=active_cit>' + cit_spl [0] + '</span>'
                str_out += ctxL [ii + 1]
            context ['context'] = str_out
        else:
            context ['answer']  =  vdbe.lft_lemma_display + ' = ' + vdbe.rgt_lemma_display
#            context ['context'] =  vdbe.get_lft_ctx_str ()
            citL = vdbe.get_citL ()
            ctxL = vdbe.get_ctxL ()
            str_out = ctxL [0]

            for ii in range (len (citL)):
                cit_spl = [w.strip () for w in citL[ii].split ('=')]
                str_out += '<span class=active_cit>' + cit_spl [0] + '</span>'
                str_out += ctxL [ii + 1]
            context ['context'] = str_out

        context ['answer'] = '<span class=lemma>' +  context ['answer'] + '</span>'

#            answer_str = vdbe.lft_lemma + ' = ' + vdbe.rgt_lemma + 2*'\n' + vdbe.get_lft_ctx_str ()



        context['session_size'] = len (ss)
        context['rhn'] = ss.get_cur_entry_rhn ()


        return context


class ApproveButtonOnClick (RedirectView):

    def get_redirect_url (self, *args, **kwargs):
        ss = session ()
        ss.from_json (self.request.session ['ss'])
        if ss.running:
            return reverse ("fcards:user_guessing")
        else:
            return reverse ("fcards:end_of_session")



    def get(self, request, *args, **kwargs ):
        print ("mydebug >>> ApproveButtonOnClick")

        ss = session ()
        ss.from_json (request.session ['ss'])
        ss.handle_hit ()
        request.session ['ss'] = ss.to_json ()

        return super().get (request, *args, **kwargs) # pass it on upwards


class DontApproveButtonOnClick (RedirectView):

    def get_redirect_url (self, *args, **kwargs):
        return reverse ("fcards:user_guessing")

    def get(self, request, *args, **kwargs):

        #print ("mydebug >>> DontApproveButtonOnClick")
        ss = session ()
        ss.from_json (request.session ['ss'])
        ss.handle_miss ()
        request.session ['ss'] = ss.to_json ()

        return super().get (request, *args, **kwargs) # pass it on upwards
