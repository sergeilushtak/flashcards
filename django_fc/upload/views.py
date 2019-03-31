from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.urls import reverse

from fc_engine.db_voc import dbVoc
from fc_engine.settings import Settings
from fcards.models import VocEntry, all_to_dbvoc, User, FCSettings
import codecs
from text.models import MyTextFilesModel

from common.db_voc2voc_entry_db import db_voc2voc_entry_db, save_file

import time

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():

            uploaded_file = request.FILES['file']
            utf8_str = uploaded_file.read ().decode ('utf-8')

            stt = Settings ()
            stt.from_json (request.session ['stt'])

            new_db_voc = dbVoc ()
            print ('time: {}'.format (time.asctime (time.localtime (time.time()))))
            new_db_voc.from_text (utf8_str, stt.extract_sentences)
            print ('time: {}'.format (time.asctime (time.localtime (time.time()))))

            #print ('mydebug>>>> upload_file : file: {}'.format (form.cleaned_data ['file']))

            if 'save_value' in request.POST:
                save = request.POST ['save_file']
            else:
                save = False
                
            project_id = request.session ['project_id']
            if save:
                file_name = str (form.cleaned_data ['file'])
                save_file (utf8_str, file_name, request.user.id, project_id)

            #action = request.POST ['action']
            action = 'overwrite'

            db_voc2voc_entry_db (action, new_db_voc, request.user.id, project_id)

            print ('time: {}'.format (time.asctime (time.localtime (time.time()))))

        else:
            print ("Form invalid")

        return HttpResponseRedirect (reverse('home'))
    else:
        form = UploadFileForm()
        return render(request, 'upload_file.html', {'form': form})
