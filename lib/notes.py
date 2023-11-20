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
    if (len(subject) == 0): raise ValueError("Subject cannot be empty!")
    if(db.GetNote(user.uuid,subject) is not None): raise ValueError("Subject name already in use!")

    newNote = Note(user.uuid,subject,text)
    if(newNote is not None): db.InsertNote(newNote)
    
    return newNote


def GetNoteFromDBResult(result:list) -> Note:
    if (result is None): return None
    hidden = bool(result[5])
    if (hidden): return None

    note = Note(result[0],result[1],result[2],result[3])
    note.creationTimeUTC = datetime.strptime(result[4],'%Y-%m-%d %H:%M:%S.%f')

    return note


def GetNote(ownerUUID: uuid.UUID, subject: str) -> Note:
    noteData = db.GetNote(ownerUUID,subject)
    note = GetNoteFromDBResult(noteData)
    return note

def GetAllUserNotes(ownerUUID: uuid.UUID) -> list[Note]:
    result = []
    notes = db.LoadAllUserNotes(ownerUUID)
    for note in notes:
        note = GetNoteFromDBResult(note)
        if (note is None): continue
        result.append(note)

    return result


def RemoveNote(ownerUUID: uuid.UUID, subject: str) -> None:
    result = db.RemoveNote(ownerUUID,subject)
    if (result.rowcount == 0): raise Exception("No note found to be removed!")


def UpdateNote(note: Note) -> None:
    result = db.UpdateNote(note)
    if (result.rowcount == 0): raise Exception("Failed to update note!")

def RemoveAllUserNotes(ownerUUID: uuid.UUID) -> int:
    """Returns the number of notes removed"""
    result = db.RemoveAllUserNotes(ownerUUID)
    return result.rowcount


def FindNotes(ownerUUID: uuid.UUID, what: str, type: str) -> list[Note]:
    notesData = db.FindNote(ownerUUID,what,type)
    notes = []
    for rawNote in notesData:
        note = GetNoteFromDBResult(rawNote)
        if (note is not None): notes.append(note)

    return notes