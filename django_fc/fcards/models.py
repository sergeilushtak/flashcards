from django.db import models

# Create your models here.
from fc_engine.voc_db_entry import VocDBEntry
from fc_engine.db_voc import dbVoc
from fc_engine.settings import Settings

from collections import defaultdict

from django.contrib.auth import get_user_model
User = get_user_model()


class VocEntry (models.Model, VocDBEntry):

    user = models.ForeignKey(User, related_name="entries", on_delete=models.CASCADE)
    date = models.CharField (max_length=20)
    lemma_ID = models.CharField (max_length=50)
    lft_lemma = models.CharField (max_length=50)
    correct_answer = models.CharField (max_length=50)
    rgt_lemma = models.CharField (max_length=50)
    cits = models.CharField (max_length=1000)
    ctxs = models.CharField (max_length=1000)
    times_asked = models.CharField (max_length=20)


    def to_vdbe (self):
        vdbe = VocDBEntry ()

        vdbe.ID = self.id
        vdbe.date = self.date
        vdbe.lemma_ID = self.lemma_ID
        vdbe.lft_lemma = self.lft_lemma
        vdbe.correct_answer = self.correct_answer
        vdbe.rgt_lemma = self.rgt_lemma
        vdbe.cits = self.cits
        vdbe.ctxs = self.ctxs
        vdbe.times_asked = int(self.times_asked)

        return vdbe

    def from_vdbe (self, vdbe):


        self.date = vdbe.date
        self.lemma_ID = vdbe.lemma_ID
        self.lft_lemma = vdbe.lft_lemma
        self.correct_answer = vdbe.correct_answer
        self.rgt_lemma = vdbe.rgt_lemma
        self.cits = vdbe.cits
        self.ctxs = vdbe.ctxs
        self.times_asked = vdbe.times_asked


from fc_engine.globals import stt

def get_vdbe (id):
    return VocEntry.objects.get (id=id).to_vdbe ()


def all_to_dbvoc (user_id):
    global stt


    all = VocEntry.objects.filter(user_id=user_id)

    db_voc = dbVoc ()

    lemma_id2count = defaultdict (int)
    for ve in all:
        lemma_id2count [ve.lemma_ID] += 1

    for ve in all:
        if lemma_id2count [ve.lemma_ID] >= stt.voc.frequency:
            vdbe = ve.to_vdbe ()
            db_voc.add_entry (vdbe)

    db_voc.complete ()
    return db_voc

#----------------------------------------------
class FCSettings (models.Model):
    user        = models.ForeignKey(User, related_name="settings", on_delete=models.CASCADE)
    chunk_size  =  models.IntegerField ()
    mode        =  models.CharField (max_length=4)
    voc_freq    =  models.IntegerField ()
    punitive_rhn =  models.IntegerField ()
    initial_rhn =  models.IntegerField ()

    def from_stt (self, stt):
        #if stt.db_id != -1:
        #    self.id = stt.db_id

        self.mode         = stt.session.mode
        self.punitive_rhn = stt.session.rhn_punitive
        self.initial_rhn  = stt.session.rhn_initial

        self.chunk_size = stt.chunk.size
        self.voc_freq   = stt.voc.frequency

    def to_stt (self):
        stt = Settings ()
        stt.db_id = self.id
        stt.chunk.size = self.chunk_size
        stt.session.mode = self.mode
        stt.session.rhn_punitive = self.punitive_rhn
        stt.session.rhn_initial = self.initial_rhn
        return stt
