from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.urls import reverse

from fc_engine.db_voc import dbVoc
from fcards.models import VocEntry, all_to_dbvoc, User
import codecs
from text.models import MyTextFilesModel

from common.db_voc2voc_entry_db import db_voc2voc_entry_db, save_file


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():

            uploaded_file = request.FILES['file']
            utf8_str = uploaded_file.read ().decode ('utf-8')

            new_db_voc = dbVoc ()

            new_db_voc.from_text (utf8_str)

            #print ('mydebug>>>> upload_file : file: {}'.format (form.cleaned_data ['file']))

            save_file = request.POST ['save_file']
            if save_file:
                file_name = str (form.cleaned_data ['file'])
                save_file (utf8_str, file_name, request.user.id)

            action = request.POST ['action']

            db_voc2voc_entry_db (action, new_db_voc, request.user.id)
        else:
            print ("Form invalid")

        return HttpResponseRedirect (reverse('home'))
    else:
        form = UploadFileForm()
        return render(request, 'upload_file.html', {'form': form})
