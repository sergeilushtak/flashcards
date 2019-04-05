from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse

from .forms import SettingsForm
from . import forms

import fcards
from fcards.models import FCSettings
from fcards.models import VocEntry, Project, Language
from fc_engine.settings import Settings
from text.models import MyTextFilesModel

from fc_engine.floating_window import FloatingWindow

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
                try:
                    project_obj = Project.objects.filter (user_id=self.request.user.id).get (id=project_id)
                except Project.DoesNotExist:
                    del (self.request.session ['project_id'])
                    print ("mydebug >>> [E] : project of specified id doesn't exit. Cleaning up")

            if 'project_id' in self.request.session:

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
                # Work with source files menu

                files = MyTextFilesModel.objects.filter (user_id=self.request.user.id, project_id=project_id)
                context ['txt_files'] = files
                try:
                    current_file = MyTextFilesModel.objects.get (
                        user_id=self.request.user.id
                        , project_id=project_id
                        , current = True
                        )
                    #print ("django_fc.views. Found current file")
                    context ['current_file'] = current_file.file_name
                except MyTextFilesModel.DoesNotExist:
                    pass


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

                all_voc = fcards.models.all_to_dbvoc (self.request.user.id, project_id)
                date_count = all_voc.get_date_cnt ()

                context ['date_count'] = date_count


                str_dates = all_voc.get_dateL ()


                ecounts = [len (all_voc.get_dated_idL (date)) for date in str_dates]

                debug_dates = True
                if debug_dates:
                    print ("mydebug>>> views.HomePage.get_context_data. dates found. total {}".format (date_count))
                    for ii in range (len (str_dates)):
                        print ("entry_count [{}] = {}".format (str_dates [ii], ecounts [ii]))
                    print ()


                context ['stt_session_mode'] = stt.session.mode

                entry_count = all_voc.get_size ()

                context ['entry_count'] = entry_count

                str_dates.reverse ()
                ecounts.reverse ()

                if len (str_dates) > 0:
                    if not (len (str_dates) == 1 and str_dates [0] == 'NO_DATE'):
                        context ['latest_date'] = str_dates [0]
                        context ['latest_date_ecount'] = ecounts [0]

                if len (str_dates) > 1:
                    context ['prev_date'] = str_dates [1]
                    context ['prev_date_ecount'] = ecounts [1]

                class date_thing ():
                    def __init__ (self, date, ecount):
                        self.str_date = date
                        self.ecount = ecount
                if len (str_dates) > 2:

                    #context ['date_list'] = str_dates [2:]
                    #context ['ecount_list'] = ecounts [2:]
                    date_things = []
                    for ii in range (2, len (str_dates)):
                        date_things.append (date_thing (str_dates [ii], ecounts [ii]))

                    context ['date_thing_list'] = date_things

            #floating window
                all_voc = fcards.models.all_to_dbvoc (self.request.user.id, project_id)
                try:
                    dbfwindex = fcards.models.FloatingWindowIndex.objects.get (
                            project_id=project_id,
                            user_id=self.request.user.id)
                    fw_index = dbfwindex.index


                except fcards.models.FloatingWindowIndex.DoesNotExist:
                    fw_index = 0
                    dbfwindex = fcards.models.FloatingWindowIndex ()
                    dbfwindex.index = fw_index
                    dbfwindex.project_id = project_id
                    dbfwindex.user_id = self.request.user.id
                    dbfwindex.save ()

                if entry_count > 0:

                    fw = FloatingWindow (stt, entry_count, fw_index)

                    context ['session_state'] = 'Session {} of {}'.format (fw_index + 1, fw.get_total_step_cnt ())

                    context ['new_lesson'] = 'Lesson {} of {}'.format (fw_index + 1, fw.get_lesson_cnt ())
                    context ['is_there_new'] = fw.is_there_new ()
                    context ['is_there_prev'] = fw.is_there_prev ()
                    context ['is_there_window'] = fw.is_there_window ()

                    context ['window_start'] = fw.get_cur_window ().start
                    context ['window_size'] = fw.get_cur_window ().size
                    context ['is_there_window'] = fw.is_there_window ()

                    context ['new_start'] = fw.get_cur_new ().start
                    context ['new_size'] = fw.get_cur_new ().size

                    context ['prev_start'] = fw.get_cur_prev ().start
                    context ['prev_size'] = fw.get_cur_prev ().size

                    context ['not_at_start'] = not fw.is_at_start ()
                    context ['not_at_end'] = not fw.is_at_end ()


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


#------------------------- floating_window

def fw_move_back (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    project_id = request.session ['project_id']
    all_voc = fcards.models.all_to_dbvoc (request.user.id, project_id)


    #print ('mydebug>>>>>> start_new_floating_window : len (all_voc)'.format (len (all_voc)))

    dbfwindex = fcards.models.FloatingWindowIndex.objects.get (project_id=project_id, user_id=request.user.id)
    fw_index = dbfwindex.index

    floating_window = FloatingWindow (stt, len (all_voc), fw_index)
    if not floating_window.is_at_start ():
        fw_index = floating_window.cur - 1

    dbfwindex.index = fw_index
    dbfwindex.save ()

    return HttpResponseRedirect (reverse('home'))

def fw_move_forward (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    project_id = request.session ['project_id']
    all_voc = fcards.models.all_to_dbvoc (request.user.id, project_id)


    #print ('mydebug>>>>>> start_new_floating_window : len (all_voc)'.format (len (all_voc)))


    dbfwindex = fcards.models.FloatingWindowIndex.objects.get (project_id=project_id, user_id=request.user.id)
    fw_index = dbfwindex.index

    floating_window = FloatingWindow (stt, len (all_voc), fw_index)
    if not floating_window.is_at_end ():
        fw_index = floating_window.cur + 1

    dbfwindex.index = fw_index
    dbfwindex.save ()



    return HttpResponseRedirect (reverse('home'))

def fw_move_to_start (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    project_id = request.session ['project_id']
    all_voc = fcards.models.all_to_dbvoc (request.user.id, project_id)


    #print ('mydebug>>>>>> start_new_floating_window : len (all_voc)'.format (len (all_voc)))


    dbfwindex = fcards.models.FloatingWindowIndex.objects.get (project_id=project_id, user_id=request.user.id)

    dbfwindex.index = 0
    dbfwindex.save ()


    return HttpResponseRedirect (reverse('home'))


def edit_settings (request):

    stt = Settings ()
    stt.from_json (request.session ['stt'])
    project_id = request.session ['project_id']

    form = forms.SettingsForm (stt)

    if request.method == 'POST':
        form = forms.SettingsForm (stt, request.POST)
        if form.is_valid ():
            form.to_stt (stt)
            dbst = FCSettings.objects.get (user_id=request.user.id, project_id=project_id )
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

def edit_project (request):

    project_id = request.session ['project_id']
    project = Project.objects.get (id = project_id)

    form = forms.EditProjectForm (project)

    if request.method == 'POST':
        form = forms.EditProjectForm (project, request.POST)
        if form.is_valid ():
#            project = Project ()
            project.name = form.cleaned_data ['name']
            language_obj = Language.objects.get (name=form.cleaned_data ['language'])
            project.language_id = language_obj.id
            project.user_id = request.user.id
            project.secret = not form.cleaned_data ['allow_sharing']
            project.save ()

#            fc_settings = FCSettings ()
#            fc_settings.project_id = project.id
#            fc_settings.user_id = request.user.id

#            stt = Settings ()
#            fc_settings.from_stt (stt)
#            request.session ['stt'] = stt.to_json ()
#            fc_settings.save ()


#            request.session ['project_id'] = project.id

            return  HttpResponseRedirect (reverse ("home"))

    return render (request, 'edit_project.html', {'form':form})

def delete_project (request, *args, **kwargs):

    print ('mydebug>>> delete_project called')
    project_id = request.session ['project_id']
    project = Project.objects.get (id = project_id)
    project.delete ()
    del (request.session ['project_id'])

    return  HttpResponseRedirect (reverse ("home"))


#----------------------------------- end of projects


class TestPage(TemplateView):
    template_name = 'test.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'
