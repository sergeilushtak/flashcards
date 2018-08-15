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
            new_db_voc = dbVoc ()
            new_db_voc.from_text (txt)

            with codecs.open (file_name + '_' + str (request.user.id), 'w', 'utf8') as fout:
                fout.write (txt)

            try :
                db_entry = MyTextFilesModel.objects.get (file_name=file_name)
            except:
                db_entry = MyTextFilesModel ()

            db_entry.user_id = request.user.id
            db_entry.file_name = file_name
            db_entry.save ()

            if request.POST ['aggregate'] == 'append_dates':

                dateS = set ()
                for d in list (VocEntry.objects.values ('date').distinct()):
                    dateS.add (d ['date'])

                for new_date in new_db_voc.dateL:
                    if new_date not in dateS:
                        for id in sorted (new_db_voc.date2idL [new_date]):
                            ventry = VocEntry ()
                            ventry.from_vdbe (new_db_voc.id2vdbe [id])
                            ventry.user_id = request.user.id
                            ventry.save()
            else:
                if request.POST ['aggregate'] == 'overwrite':
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


    return render (request, 'work_with_text.html', {'form':form})
