from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.urls import reverse

from fc_engine.db_voc import dbVoc
from fcards.models import VocEntry, all_to_dbvoc, User
import codecs
from text.models import MyTextFilesModel

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():

            uploaded_file = request.FILES['file']
            utf8_str = uploaded_file.read ().decode ('utf-8')

            new_db_voc = dbVoc ()

            new_db_voc.from_text (utf8_str)
#            new_db_voc.from_uploaded_file (uploaded_file)


            #print ('mydebug>>>> upload_file : file: {}'.format (form.cleaned_data ['file']))

            save_file = request.POST ['save_file']
            if save_file:
                file_name = str (form.cleaned_data ['file'])
                raw_file_name = file_name  + '_' + str (request.user.id)

                with codecs.open (raw_file_name, 'w', 'utf8') as fout:
                    fout.write (utf8_str)

                db_entries = MyTextFilesModel.objects.filter (user_id=request.user.id).filter(file_name=file_name)
                if len (db_entries) > 1:
                    db_entries.delete ()

                if len (db_entries) == 0 or len (db_entries) > 1:
                    db_entry = MyTextFilesModel ()
                    db_entry.user_id = request.user.id
                    db_entry.file_name = file_name
                    db_entry.save ()

            action = request.POST ['action']

            if action == 'add_dates' or action == 'replace_dates':
                old_dateS = set ()
                for d in list (VocEntry.objects.filter (user_id=request.user.id).values ('date').distinct()):
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
                    all = VocEntry.objects.filter (user_id=request.user.id)
                    all .delete ()
                    """
                    print ('--------------------------------')
                    #print (User ().username)
                    print (request.user.id)
                    print ("=================================")
                    print  (len (all))
                    """


                for _, vdbe in sorted (new_db_voc.id2vdbe.items ()):
                    #print (vdbe)
                    ventry = VocEntry ()
                    ventry.from_vdbe (vdbe)
                    ventry.user_id = request.user.id
                    ventry.save()

        else:
            print ("Form invalid")

        return HttpResponseRedirect (reverse('home'))
    else:
        form = UploadFileForm()
        return render(request, 'upload_file.html', {'form': form})
