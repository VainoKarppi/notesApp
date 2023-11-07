from datetime import datetime
import lib.accounts as accounts
import lib.sqlitedb as db
import uuid

import os
import json
from uuid import UUID



#! ----------------------
#! NOTES FUNCTIONS
#! ----------------------
class Note:
    def __init__(self, ownerUUID: uuid.UUID, subject: str, text: str, webPage: str = ""):
        self.ownerUUID = ownerUUID
        self.subject = subject
        self.text = text
        self.webPage = webPage
        self.creationTimeUTC = datetime.utcnow()
        self.hidden = False

    def __str__(self):
        return(f"\townerUUID: {self.ownerUUID}\n\tsubject: {self.subject}\n\ttext: {self.text}\n\twebPage: {self.webPage}\n\tcreationTimeUTC: {self.creationTimeUTC}\n")


def CreateNote(user: accounts.Account, subject: str, text: str) -> Note:
    if(db.GetNote(user.uuid,subject) is not None): raise ValueError("Subject name already in use!")

    newNote = Note(user.uuid,subject,text)
    return newNote


def GetNoteFromDBResult(result:list) -> Note:
    hidden = bool(result[5])
    if (hidden): return None

    note = Note(result[0],result[1],result[2],result[3])
    note.creationTimeUTC = datetime.strptime(result[4],'%Y-%m-%d %H:%M:%S.%f')

    return note


def GetNote(ownerUUID: uuid.UUID, subject: str) -> Note:
    noteData = db.GetNote(ownerUUID,subject)
    note = GetNoteFromDBResult(noteData)
    return note



