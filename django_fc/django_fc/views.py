from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse

from .forms import SettingsForm
from . import forms
#from fcards.views import stt
#from fc_engine.globals import stt
from fcards.models import FCSettings
from fcards.models import VocEntry, Project, Language
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

        #Project
        project_selected = False
        if self.request.user.id != None:
            if 'project_id' in self.request.session:
                project_id = self.request.session ['project_id']
                project_obj = Project.objects.filter (user_id=self.request.user.id).get (id=project_id)
                project_name = project_obj.name
                language_obj = Language.objects.get (id=project_obj.language_id)
                language_name = language_obj.name
                language_id = language_obj.id

                context ['project'] = project_name
                context ['language'] = language_name
                project_selected = True

            context ['projects'] = Project.objects.filter (user_id=self.request.user.id)
            print ("views:index: projects found: ")
            for pr in context ['projects']:
                print ('\t{}'.format (pr.name))
        #Settings
        if project_selected:
            print ("views.index : project selected. Name: {}".format (project_name))

            stt = Settings ()

            print ("mydebug >>> HomePage.get_context_data user_id : {}".format (self.request.user.id))

            if self.request.user.id != None:
                # Work with text menu
                files = MyTextFilesModel.objects.filter (user_id=self.request.user.id, project_id=project_id)
                context ['txt_files'] = files

                #settings

                try:
                    dbst = FCSettings.objects.get (user_id=self.request.user.id, project_id=project_id)
                    #print ("mydebug >>> HomePage.get_context_data dbst.mode = {}".format (dbst.mode))
                    stt = dbst.to_stt ()
                    #print ("mydebug >>> HomePage.get_context_data created stt. stt.mode = {}".format (stt.session.mode))

                except FCSettings.DoesNotExist:
                    dbst = FCSettings ()
                    dbst.from_stt (stt)
                    dbst.project_id = project_id
                    print ("mydebug >>> HomePage.get_context_data created FCSettings entry.")
                    dbst.user_id = self.request.user.id
                    dbst.save ()

                except FCSettings.MultipleObjectsReturned:
                    print ("mydebug >>> HomePage.get_context_data deleting settings from db")
                    FCSettings.objects.filter (user_id=self.request.user.id, project_id=project_id).delete ()

                    dbst = FCSettings ()
                    dbst.from_stt (stt)
                    print ("mydebug >>> HomePage.get_context_data created FCSettings entry.")
                    dbst.user_id = self.request.user.id
                    dbst.project_id = project_id
                    dbst.save ()

                self.request.session ['stt'] = stt.to_json ()
            #sessions

                date_count = VocEntry.objects.filter (user_id=self.request.user.id, project_id=project_id).values ('date').distinct().count ()
                context ['date_count'] = date_count

                str_dates = []
                str_ecounts = []

                dates = VocEntry.objects.filter (user_id=self.request.user.id, project_id=project_id).values ('date').distinct()
                for date in dates:
                    date = date ['date']
                    e_count = VocEntry.objects.filter (user_id=self.request.user.id, project_id=project_id).filter (date=date).count ()

                    str_dates.append (date)
                    str_ecounts.append (str (e_count))

                debug_dates = True
                if debug_dates:
                    print ("mydebug>>> views.HomePage.get_context_data. dates found. total {}".format (date_count))
                    for ii in range (len (str_dates)):
                        print ("entry_count [{}] = {}".format (str_dates [ii], str_ecounts [ii]))
                    print ()


                context ['stt_session_mode'] = stt.session.mode

                entry_count = VocEntry.objects.filter (user_id=self.request.user.id, project_id=project_id).count ()


                context ['entry_count'] = entry_count

                str_dates.reverse ()
                str_ecounts.reverse ()

                if len (str_dates) > 0:
                    context ['latest_date'] = str_dates [0]
                    context ['latest_date_ecount'] = str_ecounts [0]

                if len (str_dates) > 1:
                    context ['prev_date'] = str_dates [1]
                    context ['prev_date_ecount'] = str_ecounts [1]

                if len (str_dates) > 2:
                    context ['date_list'] = str_dates [2:]

        return context


def toggle_stt_session_mode (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])

    if stt.session.mode == 'generation':
        stt.session.mode = 'recognition'
    else:
        stt.session.mode = 'generation'

    #print ('mydebug>>>>>> toggle_stt_session_mode : stt.session.mode = {}'.format (stt.session.mode))

#    request.session ['stt'] = stt.to_json ()
    project_id = request.session ['project_id']

    dbst = FCSettings.objects.get (user_id=request.user.id, project_id=project_id)
    dbst.from_stt (stt)

    #print ('mydebug>>>>>> toggle_stt_session_mode : dbst.mode = {}'.format (dbst.mode))

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


#----------------------- projects projects projects

def select_project (request, *args, **kwargs):
    name = kwargs ['name']
    project = Project.objects.filter (user_id=request.user.id).get (name=name)
    request.session ['project_id'] = project.id

    return  HttpResponseRedirect (reverse ("home"))


def new_project (request):

    form = forms.NewProjectForm ()

    if request.method == 'POST':
        form = forms.NewProjectForm (request.POST)
        if form.is_valid ():
            project = Project ()
            project.name = form.cleaned_data ['name']
            language_obj = Language.objects.get (name=form.cleaned_data ['language'])
            project.language_id = language_obj.id
            project.user_id = request.user.id
            project.secret = not form.cleaned_data ['allow_sharing']
            project.save ()

            fc_settings = FCSettings ()
            fc_settings.project_id = project.id
            fc_settings.user_id = request.user.id

            stt = Settings ()
            fc_settings.from_stt (stt)
            request.session ['stt'] = stt.to_json ()
            fc_settings.save ()


            request.session ['project_id'] = project.id

            return  HttpResponseRedirect (reverse ("home"))

    return render (request, 'new_project.html', {'form':form})


class TestPage(TemplateView):
    template_name = 'test.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'
