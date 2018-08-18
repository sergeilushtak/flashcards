from fcards.models import VocEntry
from text.models import MyTextFilesModel
import codecs

def db_voc2voc_entry_db (action, new_db_voc, user_id):

        if action == 'add_dates':
            old_dateS = set ()
            for d in list (VocEntry.objects.filter(user_id=user_id).values ('date').distinct()):
                old_dateS.add (d ['date'])

            def add_dated_section (idL, id2vdbe, user_id):
                for id in sorted (idL):
                    ventry = VocEntry ()
                    ventry.from_vdbe (id2vdbe [id])
                    ventry.user_id = user_id
                    ventry.save()

            for new_date in new_db_voc.dateL:
                if new_date not in old_dateS:
                    #date2Id is ok here because all entries are new.
                    add_dated_section (new_db_voc.date2idL [new_date], new_db_voc.id2vdbe, user_id)


        else:
            if action == 'overwrite':
                print ('--------------------------------')
                #print (User ().username)
                print (user_id)
                print ("=================================")
                all = VocEntry.objects.filter (user_id=user_id)
                print  (len (all))
                all .delete ()


            for _, vdbe in sorted (new_db_voc.id2vdbe.items ()):
                #print (vdbe)
                ventry = VocEntry ()
                ventry.from_vdbe (vdbe)
                ventry.user_id = user_id
                ventry.save()


def save_file (txt, file_name, user_id):

    raw_file_name = file_name + '_' + str (user_id)
    with codecs.open (raw_file_name, 'w', 'utf8') as fout:
        fout.write (txt)

    if MyTextFilesModel.objects.filter (file_name=file_name, user_id=user_id).count () == 0:
        db_entry = MyTextFilesModel ()

        db_entry.user_id = user_id
        db_entry.file_name = file_name
        db_entry.save ()
