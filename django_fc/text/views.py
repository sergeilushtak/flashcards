from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse
import codecs

from . import forms
from . import models

from fc_engine.db_voc import dbVoc
from fcards.models import VocEntry
from .models import MyTextFilesModel

from common.db_voc2voc_entry_db import db_voc2voc_entry_db, save_file

def work_with_text (request, *args, **kwargs):

    file_name = kwargs ['file_name']
    if len (file_name) > 0:
        raw_file_name = file_name + '_' + str (request.user.id)

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

                new_db_voc = dbVoc ()
                new_db_voc.from_text (txt)

                project_id = request.session ['project_id']
                if save_the_file:
                    save_file (txt, file_name, request.user.id, project_id)

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

                #need to check here is new_file_name is valid

                return  HttpResponseRedirect (reverse ("text:work_with_text", kwargs={'file_name' : new_file_name}))


    return render (request, 'work_with_text.html', {'form':form, 'file_name':file_name})

import os

def delete_file (request, *args, **kwargs):

    print ('mydebug>>> delete_file called')
    file_name = kwargs ['file_name']
    print ('mydebug>>> delete_file : file_name : {}'.format (file_name))

    raw_file_name = file_name + '_' + str (request.user.id)

    if os.path.isfile (raw_file_name):
        os.remove (raw_file_name)
        db_entries = MyTextFilesModel.objects.filter (file_name=file_name)
        if len (db_entries) > 1:
            print ("text.views.delete_file: [W] : there were more than one entries in file db with file_name: " + file_name)
        db_entries.delete ()
    else:
        print ('mydebug>>> delete_file : {} doesn\'t exist'.format (file_name))

    return  HttpResponseRedirect (reverse ("home"))
