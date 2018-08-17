from django.shortcuts import render,HttpResponseRedirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse
import codecs

from . import forms
from . import models

from fc_engine.db_voc import dbVoc
from fcards.models import VocEntry
from .models import MyTextFilesModel

# Create your views here.
this_file = 'file_file.txt'
def work_with_text (request, *args, **kwargs):

    print ("kwargs: " + str (kwargs))
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
        if form.is_valid ():

            txt = form. cleaned_data ['text']
            file_name = form.cleaned_data ['file_name']
            save_file = form.cleaned_data ['save_file']

            new_db_voc = dbVoc ()
            new_db_voc.from_text (txt)


            if save_file:
                with codecs.open (file_name + '_' + str (request.user.id), 'w', 'utf8') as fout:
                    fout.write (txt)

            try :
                db_entry = MyTextFilesModel.objects.get (file_name=file_name)
            except:
                db_entry = MyTextFilesModel ()

            db_entry.user_id = request.user.id
            db_entry.file_name = file_name
            db_entry.save ()

            action = request.POST ['action']

            if action == 'add_dates' or action == 'replace_dates':
                old_dateS = set ()
                for d in list (VocEntry.objects.filter(user_id=request.user.id).values ('date').distinct()):
                    old_dateS.add (d ['date'])

                def add_dated_section (idL, id2vdbe, user_id):
                    for id in sorted (idL):
                        ventry = VocEntry ()
                        ventry.from_vdbe (id2vdbe [id])
                        ventry.user_id = user_id
                        ventry.save()

                for new_date in new_db_voc.dateL:
                    if new_date not in old_dateS:
                        add_dated_section (new_db_voc.date2idL [new_date], new_db_voc.id2vdbe, request.user.id)

                    elif action == 'replace_dates':
                        old_dated_section = VocEntry.objects.filter (user_id=request.user.id).filter(date=new_date)
                        old_dated_section.delete ()
                        add_dated_section (new_db_voc.date2idL [new_date], new_db_voc.id2vdbe, request.user.id)


            else:
                if request.POST ['action'] == 'overwrite':
                    print ('--------------------------------')
                    #print (User ().username)
                    print (request.user.id)
                    print ("=================================")
                    all = VocEntry.objects.filter (user_id=request.user.id)
                    print  (len (all))
                    all .delete ()


                for _, vdbe in sorted (new_db_voc.id2vdbe.items ()):
                    #print (vdbe)
                    ventry = VocEntry ()
                    ventry.from_vdbe (vdbe)
                    ventry.user_id = request.user.id
                    ventry.save()

        else:
            print ("Form invalid")

        return  HttpResponseRedirect (reverse ("home"))


    return render (request, 'work_with_text.html', {'form':form, 'file_name':file_name})

import os

def delete_file (request, *args, **kwargs):

    print ('mydebug>>> delete_file called')
    file_name = kwargs ['file_name']
    print ('mydebug>>> delete_file : file_name : {}'.format (file_name))

    raw_file_name = file_name + '_' + str (request.user.id)

    if os.path.isfile (raw_file_name):
        os.remove (raw_file_name)
        db_entry = MyTextFilesModel.objects.get (file_name=file_name)
        db_entry.delete ()
    else:
        print ('mydebug>>> delete_file : {} doesn\'t exist'.format (file_name))

    return  HttpResponseRedirect (reverse ("home"))
