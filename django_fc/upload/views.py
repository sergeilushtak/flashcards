from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.urls import reverse

from fc_engine.db_voc import dbVoc
from fcards.models import VocEntry, all_to_dbvoc, User

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():

            uploaded_file = request.FILES['file']
            new_db_voc = dbVoc ()
            new_db_voc.from_uploaded_file (uploaded_file)


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

        return HttpResponseRedirect (reverse('home'))
    else:
        form = UploadFileForm()
        return render(request, 'upload_file.html', {'form': form})
