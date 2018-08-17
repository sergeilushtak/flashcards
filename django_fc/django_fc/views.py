from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse

from .forms import SettingsForm
from . import forms
#from fcards.views import stt
#from fc_engine.globals import stt
from fcards.models import FCSettings
from fcards.models import VocEntry
from fc_engine.settings import Settings
from text.models import MyTextFilesModel

class HomePage(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
#        print ("Home Page.get: user id = {}".format (request.user.id))
        ret = super().get(request, *args, **kwargs)
#        print ("Home Page.get: about to return")
        return ret

    def get_context_data(self,**kwargs):
        context  = super().get_context_data(**kwargs)


        #Settings

        stt = Settings ()

        print ("mydebug >>> HomePage.get_context_data user_id : {}".format (self.request.user.id))

        if self.request.user.id != None:
            # Work with text menu
            files = MyTextFilesModel.objects.filter (user_id=self.request.user.id)
            context ['txt_files'] = files

            #settings

            try:
                dbst = FCSettings.objects.get (user_id=self.request.user.id)
                #print ("mydebug >>> HomePage.get_context_data dbst.mode = {}".format (dbst.mode))
                stt = dbst.to_stt ()
                #print ("mydebug >>> HomePage.get_context_data created stt. stt.mode = {}".format (stt.session.mode))

            except FCSettings.DoesNotExist:
                dbst = FCSettings ()
                dbst.from_stt (stt)
                print ("mydebug >>> HomePage.get_context_data created FCSettings entry.")
                dbst.user_id = self.request.user.id
                dbst.save ()

            except FCSettings.MultipleObjectsReturned:
                print ("mydebug >>> HomePage.get_context_data deleting settings from db")
                FCSettings.objects.filter (user_id=self.request.user.id).delete ()

                dbst = FCSettings ()
                dbst.from_stt (stt)
                print ("mydebug >>> HomePage.get_context_data created FCSettings entry.")
                dbst.user_id = self.request.user.id
                dbst.save ()

            self.request.session ['stt'] = stt.to_json ()
        #sessions

            date_count = VocEntry.objects.filter (user_id=self.request.user.id).values ('date').distinct().count ()
            context ['date_count'] = date_count


            context ['stt_session_mode'] = stt.session.mode

            entry_count = VocEntry.objects.filter (user_id=self.request.user.id).count ()

            context ['entry_count'] = entry_count

            context ['ind_list'] = range (date_count - 1, 0, -1)

        return context


def toggle_stt_session_mode (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    if stt.session.mode == 'gen':
        stt.session.mode = 'reco'
    else:
        stt.session.mode = 'gen'

    print ('mydebug>>>>>> toggle_stt_session_mode : stt.session.mode = {}'.format (stt.session.mode))

#    request.session ['stt'] = stt.to_json ()
    dbst = FCSettings.objects.get (user_id=request.user.id)
    dbst.from_stt (stt)

    print ('mydebug>>>>>> toggle_stt_session_mode : dbst.mode = {}'.format (dbst.mode))

#    dbst.user_id = request.user.id
    dbst.save ()

    return HttpResponseRedirect (reverse('home'))


def edit_settings (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    form = forms.SettingsForm (stt)

    if request.method == 'POST':
        form = forms.SettingsForm (stt, request.POST)
        if form.is_valid ():
            form.to_stt (stt)
            dbst = FCSettings.objects.get (user_id=request.user.id)
            dbst.from_stt (stt)
        #    dbst.user_id = request.user.id
            dbst.save ()
            request.session ['stt'] = stt.to_json ()

            return  HttpResponseRedirect (reverse ("home"))

    return render (request, 'edit_settings.html', {'form':form})



class TestPage(TemplateView):
    template_name = 'test.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'
