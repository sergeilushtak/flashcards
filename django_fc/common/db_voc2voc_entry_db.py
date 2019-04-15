from fcards.models import VocEntry, Project
from text.models import MyTextFilesModel
import codecs

def db_voc2voc_entry_db (action, new_db_voc, user_id, project_id):

        project_obj = Project.objects.filter (user_id=user_id).get (id=project_id)
        language_id = project_obj.language_id
        secret = project_obj.secret

        if action == 'add_dates':
            old_dateS = set ()
            for d in list (VocEntry.objects.filter(user_id=user_id).values ('date').distinct()):
                old_dateS.add (d ['date'])


            def add_dated_section (idL, id2vdbe, user_id, project_id, language_id, secret):
                for id in sorted (idL):
                    ventry = VocEntry ()
                    ventry.from_vdbe (id2vdbe [id])
                    ventry.user_id = user_id
                    ventry.project_id = project_id
                    ventry.language_id = language_id
                    ventry.secret = secret
                    ventry.save()



            for new_date in new_db_voc.dateL:
                if new_date not in old_dateS:
                    #date2Id is ok here because all entries are new.
                    add_dated_section (
                        new_db_voc.date2idL [new_date],
                        new_db_voc.id2vdbe,
                        user_id,
                        project_id,
                        language_id,
                        secret
                        )


        else:
            if action == 'overwrite':
                print ('--------------------------------')
                #print (User ().username)
                print (user_id)
                print ("=================================")
                all = VocEntry.objects.filter (user_id=user_id).filter (project_id=project_id)
                print  (len (all))
                all .delete ()


            for _, vdbe in sorted (new_db_voc.id2vdbe.items ()):
                #print (vdbe)
                ventry = VocEntry ()
                ventry.from_vdbe (vdbe)
                ventry.user_id = user_id
                ventry.project_id = project_id
                ventry.language_id = language_id
                ventry.secret = secret
                ventry.save()


def save_file (txt, file_name, user_id, project_id):

    raw_file_name = file_name + '_' + str (user_id) + '_' + str (project_id)
    with codecs.open (raw_file_name, 'w', 'utf8') as fout:
        fout.write (txt)

    try:
        db_entry = MyTextFilesModel.objects.get (
                file_name=file_name
                , user_id=user_id
                , project_id=project_id
                )

    except MyTextFilesModel.DoesNotExist:
        db_entry = MyTextFilesModel ()

    db_entry.user_id = user_id
    db_entry.project_id = project_id
    db_entry.file_name = file_name
    db_entry.save ()

def make_src_current (file_name, user_id, project_id):

    try:
        old_current_file = MyTextFilesModel.objects.get (
                    user_id=user_id
                    , project_id=project_id
                    , current=True
                    )
        old_current_file.current = False
        old_current_file.save ()

    except MyTextFilesModel.DoesNotExist:
        print ("make_src_current: [E] : Current file not found")
        pass

    except MyTextFilesModel.MultipleObjectsReturned:
        print ("make_src_current: [E] : more than one current file detected. Cleaning up.")
        current_files = MyTextFilesModel.objects.filter (
                    user_id=user_id
                    , project_id=project_id
                    , current=True
                    )
        for f in current_files:
            f.current = False
            f.save ()



    try:
        db_entry = MyTextFilesModel.objects.get (
                file_name=file_name
                , user_id=user_id
                , project_id=project_id
                )

    except MyTextFilesModel.DoesNotExist:
        db_entry = MyTextFilesModel ()

        db_entry.user_id = user_id
        db_entry.project_id = project_id
        db_entry.file_name = file_name

    db_entry.current = True
    db_entry.save ()


def make_src_non_current (file_name, user_id, project_id):
    try:
        db_entry = MyTextFilesModel.objects.get (
                file_name=file_name
                , user_id=user_id
                , project_id=project_id
                )
        db_entry.current = False
        db_entry.save ()

    except MyTextFilesModel.DoesNotExist:
        print ("make_src_non_current: [E] : file {} not found".format (file_name))
        pass


def make_current_non_current (user_id, project_id):

    try:
        old_current_file = MyTextFilesModel.objects.get (
                    user_id=user_id
                    , project_id=project_id
                    , current=True
                    )
        old_current_file.current = False
        old_current_file.save ()

    except MyTextFilesModel.DoesNotExist:
        print ("make_src_current: [I] : Current file not found")
        pass

    except MyTextFilesModel.MultipleObjectsReturned:
        print ("make_src_current: [E] : more than one current file detected. Cleaning up.")
        current_files = MyTextFilesModel.objects.filter (
                    user_id=user_id
                    , project_id=project_id
                    , current=True
                    )
        for f in current_files:
            f.current = False
            f.save ()
