from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse
import codecs

from . import forms
from . import models


from fc_engine.db_voc import dbVoc
from fc_engine.settings import Settings
from fcards.models import VocEntry
from fcards.models import FCSettings
from .models import MyTextFilesModel
import fcards
from common.db_voc2voc_entry_db import db_voc2voc_entry_db, save_file
from common.db_voc2voc_entry_db import make_src_current, make_src_non_current, make_current_non_current

def work_with_text (request, *args, **kwargs):

    file_name = kwargs ['file_name']
    if len (file_name) > 0:
        project_id = request.session ['project_id']
        raw_file_name = file_name + '_' + str (request.user.id)
        new_raw_file_name = file_name + '_' + str (request.user.id) +  '_' + str (project_id)

    if os.path.isfile (new_raw_file_name):
        fin = codecs.open (new_raw_file_name, 'r', 'utf-8');
        txt = fin.read ()
    else:
        try:

            #print ("mydebug>>> work_with_text: last_file : {}".format (last_file))
            fin = codecs.open (raw_file_name, 'r', 'utf-8');
            txt = fin.read ()


        except:
            txt = ''
            file_name = ''

    form = forms.WorkWithTextForm (txt, file_name)


    if request.method == 'POST':
        form = forms.WorkWithTextForm ('', '', request.POST)
        if 'submit_cits' in form.data:
            if form.is_valid ():

                txt = form. cleaned_data ['text']
                file_name = form.cleaned_data ['file_name']
                save_the_file = form.cleaned_data ['save_file']

                stt = Settings ()
                stt.from_json (request.session ['stt'])

                new_db_voc = dbVoc ()
                new_db_voc.from_text (txt, stt.extract_sentences)

                project_id = request.session ['project_id']
                if save_the_file:
                    save_file (txt, file_name, request.user.id, project_id)
                    make_src_current (file_name, request.user.id, project_id)
                else:
                    make_current_non_current (request.user.id, project_id)


                #action = request.POST ['action']
                action = 'overwrite'
                db_voc2voc_entry_db (action, new_db_voc, request.user.id, project_id)
            else:
                print ("Form invalid")

            return  HttpResponseRedirect (reverse ("home"))
        else:

            txt = request.POST ['text']
            #print ('txt: ' + txt)
            new_file_name = request.POST ['file_name'].strip ()
            #print ('new_file_name: ' + new_file_name)

            if len (new_file_name) > 0: # need more thorough check here
                project_id = request.session ['project_id']

                save_file (txt, new_file_name, request.user.id, project_id)
                make_src_non_current (new_file_name, request.user.id, project_id)

                #need to check here is new_file_name is valid

                return  HttpResponseRedirect (reverse ("text:work_with_text", kwargs={'file_name' : new_file_name}))


    return render (request, 'work_with_text.html', {'form':form, 'file_name':file_name})

import os

def delete_file (request, *args, **kwargs):

    print ('mydebug>>> delete_file called')
    file_name = kwargs ['file_name']
    print ('mydebug>>> delete_file : file_name : {}'.format (file_name))

    raw_file_name = file_name + '_' + str (request.user.id) + '_' + str (request.session ['project_id'])

    if os.path.isfile (raw_file_name):
        os.remove (raw_file_name)
        db_entries = MyTextFilesModel.objects.filter (file_name=file_name)
        if len (db_entries) > 1:
            print ("text.views.delete_file: [W] : there were more than one entries in file db with file_name: " + file_name)
        db_entries.delete ()


    else:
        print ('mydebug>>> delete_file : {} doesn\'t exist'.format (file_name))

    return  HttpResponseRedirect (reverse ("home"))

def generate_src_file (request):

    project_id = request.session ['project_id']
    all_voc = fcards.models.all_to_dbvoc (request.user.id, project_id)

    txt = ''
    for date in all_voc.dateL:
        txt += '\nlesson: ' + date + '\n\n'
        for ID in all_voc.date2idL [date]:

            vdbe = all_voc.id2vdbe [ID]

            ctxL = vdbe.ctxs.split ('|')
            citL = vdbe.cits.split ('|')
            strout = ctxL [0]
            for i in range (len (citL)):
                strout += citL [i]
                strout += ctxL [i + 1]
            txt += strout + '\n'

    form = forms.GenerateSourceForm (txt)
    if request.method == 'POST':

        form = forms.GenerateSourceForm ('', request.POST)

        if form.is_valid ():

            txt = form. cleaned_data ['text']
            file_name = form.cleaned_data ['file_name']
            save_file (txt, file_name, request.user.id, project_id)
            make_src_current (file_name, request.user.id, project_id)

        else:
            print ("Form invalid")

        return  HttpResponseRedirect (reverse ("home"))

    return render (request, 'generate_src_file.html', {'form':form})



from django.http import FileResponse


def download_source_file (request, *args, **kwargs):
    file_name = kwargs ['file_name']
    if len (file_name) > 0:
        project_id = request.session ['project_id']
        raw_file_name = file_name + '_' + str (request.user.id)
        new_raw_file_name = file_name + '_' + str (request.user.id) +  '_' + str (project_id)

    if os.path.isfile (new_raw_file_name):
        response = FileResponse(open(new_raw_file_name, 'rb'))
        response['Content-Disposition'] = 'attachment; filename={}'.format (file_name)
        return response
    else:
        response = FileResponse(open(raw_file_name, 'rb'), filename = file_name, as_attachment = True)

    return  HttpResponseRedirect (reverse ("home"))
