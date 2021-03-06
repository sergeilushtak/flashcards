from django.db import models

# Create your models here.
from fc_engine.db_voc import dbVoc
from fc_engine.settings import Settings

from collections import defaultdict

from fc_engine.voc_db_entry import VocDBEntry
from django.contrib.auth import get_user_model
User = get_user_model()

#----------------------------------------------

class Language (models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)

    def __str__ (self):
        return self.name


#----------------------------------------------

class Project (models.Model):
    user        = models.ForeignKey(User, related_name="projects", on_delete=models.CASCADE)
    language    = models.ForeignKey(Language, related_name="projects", on_delete=models.CASCADE, default=0)
    name        = models.CharField(max_length=50)
    secret      = models.BooleanField ()

#-----------------------------------------------------

class FloatingWindowIndex (models.Model):
    user    = models.ForeignKey(User, related_name="fw", on_delete=models.CASCADE)
    project = models.ForeignKey (Project, related_name="fw", on_delete=models.CASCADE, default=0)

    index = models.IntegerField ()


#----------------------------------------------

class VocEntry (models.Model, VocDBEntry):

    #search attributes

    user = models.ForeignKey(User, related_name="entries", on_delete=models.CASCADE)
    project = models.ForeignKey (Project, related_name="entries", on_delete=models.CASCADE, default=0)
    language = models.ForeignKey (Language, related_name="entries", on_delete=models.CASCADE, default=0)
#    project = models.CharField (max_length=50)
    secret = models.BooleanField (default=False)

    date = models.CharField (max_length=20)

    lemma_ID = models.CharField (max_length=50)

    lft_lemma_ID = models.CharField (max_length=50, default='')
    lft_usage_ID = models.CharField (max_length=50, default='')

    rgt_lemma_ID = models.CharField (max_length=50, default='')
    rgt_usage_ID = models.CharField (max_length=50, default='')


    #automatic check of user input (not supported ATM)
    correct_answer = models.CharField (max_length=50)

    #display fields
    rgt_lemma_display = models.CharField (max_length=50, default='')
    lft_lemma_display = models.CharField (max_length=50, default='')
    cits = models.CharField (max_length=1000)
    ctxs = models.CharField (max_length=1000)
    times_asked = models.CharField (max_length=20)


    def to_vdbe (self):
        vdbe = VocDBEntry ()

        vdbe.ID = self.id
        vdbe.date = self.date
        vdbe.lemma_ID = self.lemma_ID

        vdbe.lft_lemma_ID = self.lft_lemma_ID
        vdbe.rgt_lemma_ID = self.rgt_lemma_ID
        vdbe.lft_lemma_display = self.lft_lemma_display
        vdbe.rgt_lemma_display = self.rgt_lemma_display
        #vdbe.secret = self.secret

        vdbe.lft_usage_ID = self.lft_usage_ID
        vdbe.rgt_usage_ID = self.rgt_usage_ID

        vdbe.cits = self.cits
        vdbe.ctxs = self.ctxs
        vdbe.times_asked = int(self.times_asked)

        #print ('to_vdbe: date = {}'.format (vdbe.date))

        return vdbe

    def from_vdbe (self, vdbe):

        #print ('from_vdbe: date = {}'.format (vdbe.date))
        self.date = vdbe.date

        self.lemma_ID = vdbe.lemma_ID
        self.lft_lemma_ID = vdbe.lft_lemma_ID
        self.rgt_lemma_ID = vdbe.rgt_lemma_ID
        self.lft_usage_ID = vdbe.lft_usage_ID
        self.rgt_usage_ID = vdbe.rgt_usage_ID
        self.lft_lemma_display = vdbe.lft_lemma_display
        self.rgt_lemma_display = vdbe.rgt_lemma_display
        #self.secret = vdbe.secret

        self.cits = vdbe.cits
        self.ctxs = vdbe.ctxs
        self.times_asked = vdbe.times_asked



def get_vdbe (id):
    return VocEntry.objects.get (id=id).to_vdbe ()


def all_to_dbvoc (user_id, project_id):

    stt = FCSettings.objects.filter (user_id=user_id, project_id=project_id)[0].to_stt ()

#    print ()
#    print ("all_to_dbvoc:  stt_freq = {}".format (stt.voc.frequency))

    all = VocEntry.objects.filter(user_id=user_id, project_id=project_id)

    db_voc = dbVoc ()

    lemma_id2count = defaultdict (int)
    for ve in all:
        lemma_id2count [ve.lemma_ID] += 1
        #print (ve.lemma_ID)
        #print (ve.rgt_lemma_ID)

    print ('----------------')

    for ve in all:
        if lemma_id2count [ve.lemma_ID] >= stt.voc.frequency:
        #    print ('lemma_id2count [{}] = {}'.format (ve.lemma_ID, lemma_id2count [ve.lemma_ID]))
            vdbe = ve.to_vdbe ()
            db_voc.add_entry (vdbe)

    db_voc.complete ()

#    print ("all_to_dbvoc:  len(db_voc) = {}".format (len (db_voc.id2vdbe)))
#    print ()


    return db_voc

#----------------------------------------------
class FCSettings (models.Model):
    user        = models.ForeignKey(User, related_name="settings", on_delete=models.CASCADE)
    project        = models.ForeignKey(Project, related_name="settings", on_delete=models.CASCADE, default = 0)
    #chunk_size  =  models.IntegerField ()
    mode        =  models.CharField (max_length=4)
    voc_freq    =  models.IntegerField ()
    punitive_rhn =  models.IntegerField ()
    initial_rhn =  models.IntegerField ()
    randomize = models.BooleanField (default = True)

    extract_sentences = models.BooleanField ()

    fw_lesson_size = models.IntegerField (default = 10)
    fw_review_lesson_cnt = models.IntegerField (default = 6)
    lessons_rand_old = models.IntegerField (default = 60)

    def from_stt (self, stt):
        #if stt.db_id != -1:
        #    self.id = stt.db_id

        self.mode         = stt.session.mode
        self.punitive_rhn = stt.session.rhn_punitive
        self.initial_rhn  = stt.session.rhn_initial

    #    self.chunk_size = stt.chunk.size
        self.voc_freq   = stt.voc.frequency

        self.fw_lesson_size  = stt.lessons.lesson
        self.fw_review_lesson_cnt = stt.lessons.window
        self.extract_sentences = stt.extract_sentences

        self.lessons_rand_old = stt.lessons.rand_old
        self.randomize = stt.session.randomize

    def to_stt (self):
        stt = Settings ()
        stt.db_id = self.id
    #    stt.chunk.size = self.chunk_size
        stt.session.mode = self.mode
        stt.session.rhn_punitive = self.punitive_rhn
        stt.session.rhn_initial = self.initial_rhn
        stt.session.randomize = self.randomize
        #print ("fcards:models:FCSettings.to_stt :: stt.session.randomize = {}".format (stt.session.randomize))

        stt.voc.frequency = self.voc_freq

        stt.lessons.lesson = self.fw_lesson_size
        stt.lessons.window = self.fw_review_lesson_cnt
        stt.extract_sentences = self.extract_sentences

        stt.lessons.rand_old = self.lessons_rand_old

        return stt

#-----------------------------------------------------------
class ProcessedInPast (models.Model):
    user        = models.ForeignKey(User, related_name="processed_in_past", on_delete=models.CASCADE)
    project     = models.ForeignKey(Project, related_name="processed_in_past", on_delete=models.CASCADE
                , default = 0)

    lemma_ID    =  models.CharField (max_length=50)
    times_processed    =  models.IntegerField (default=1)
