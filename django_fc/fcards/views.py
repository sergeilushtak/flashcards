from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse

from . import models

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

def start_session_latest (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])


    all_voc = models.all_to_dbvoc (request.user.id)
    idL = all_voc.get_dated_idL (-1)

    ss = session ()
    if ss.start (stt, all_voc, idL):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))


def start_session_prev (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    all_voc = models.all_to_dbvoc (request.user.id)
    idL = all_voc.get_dated_idL (-2)

    ss = session ()
    if ss.start (stt, all_voc, idL):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))


def start_session_randold (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    all_voc = models.all_to_dbvoc (request.user.id)
    idL = all_voc.get_dated_idL ((0, -2))

    ss = session ()
    print ('mydebug>>>> start_session_randold : calling ss.start')
    if ss.start (stt, all_voc, idL, 20):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))


def start_session_all (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    all_voc = models.all_to_dbvoc (request.user.id)

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

    index = int (kwargs ['index']) - 1

    all_voc = models.all_to_dbvoc (request.user.id)
    idL = all_voc.get_dated_idL (index)

    ss = session ()
    if ss.start (stt, all_voc, idL):

        #eng.start ()
        #request.session ['eng']     =  eng.to_json ()
        #request.session ['all_voc'] =  all_voc.to_json ()
        request.session ['ss']      =  ss.to_json ()

        return HttpResponseRedirect(reverse('fcards:user_guessing'))
    else:
        return HttpResponseRedirect (reverse('home'))



def end_of_session (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

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

    request.session ['ss'] = ss.to_json ()

    return render(request, 'end_of_session.html', context=stats)



from  . import forms
from .models import VocEntry, get_vdbe

def edit_btn_on_click (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    ss = session ()
    ss.from_json (request.session ['ss'])
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
        print ("mydebug >>> views.UserGuessing cur_entry_ind = {}".format (ss.chunk.cur_entry_ind))
        print ("mydebug >>> views.UserGuessing cur_entry_ID = {}".format (ss.get_cur_entry_ID()))

        if stt.session.mode == 'generation':
            context ['question'] = vdbe.rgt_lemma
#            context ['context'] = vdbe.get_rgt_ctx_str ()
            citL = vdbe.get_citL ()
            ctxL = vdbe.get_ctxL ()
            str_out = ctxL [0]

            for ii in range (len (citL)):
                str_out += '<b>' + citL [ii].split (' = ') [1] + '</b>'
                str_out += ctxL [ii + 1]
    #        context ['question'] += '<br>' + str_out
            context ['context'] = str_out

        else:
            context ['question'] = vdbe.lft_lemma

        context['session_size'] = len (ss)
        context['chunk_size'] = len (ss.chunk)
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
            context ['answer'] = vdbe.rgt_lemma + ' = ' + vdbe.lft_lemma
#            context ['context'] = vdbe.get_lft_ctx_str ()
            citL = vdbe.get_citL ()
            ctxL = vdbe.get_ctxL ()
            str_out = ctxL [0]

            for ii in range (len (citL)):
                str_out += '<b>' + citL [ii].split (' = ') [0] + '</b>'
                str_out += ctxL [ii + 1]
            context ['context'] = str_out
        else:
            context ['answer']  =  vdbe.lft_lemma + ' = ' + vdbe.rgt_lemma
#            context ['context'] =  vdbe.get_lft_ctx_str ()
            citL = vdbe.get_citL ()
            ctxL = vdbe.get_ctxL ()
            str_out = ctxL [0]

            for ii in range (len (citL)):
                str_out += '<b>' + citL [ii].split (' = ') [0] + '</b>'
                str_out += ctxL [ii + 1]
            context ['context'] = str_out

#            answer_str = vdbe.lft_lemma + ' = ' + vdbe.rgt_lemma + 2*'\n' + vdbe.get_lft_ctx_str ()



        context['session_size'] = len (ss)
        context['chunk_size'] = len (ss.chunk)
        context['rhn'] = ss.get_cur_entry_rhn ()


        return context


class ApproveButtonOnClick (RedirectView):

    def get_redirect_url (self, *args, **kwargs):
        ss = session ()
        ss.from_json (self.request.session ['ss'])
        if len (ss) > 0:
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
