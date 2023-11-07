import datetime
import lib.accounts as accounts
import uuid

import os
import json
from uuid import UUID


# FIX TO ALLOW DUMP JSON UUID ENCODE
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID): return obj.hex
        return json.JSONEncoder.default(self, obj)


#! ----------------------
#! NOTES FUNCTIONS
#! ----------------------
Notes = []
class Note:
    def __init__(self, ownerUUID: uuid.UUID, subject: str, text: str):
        self.ownerUUID = ownerUUID
        self.subject = subject
        self.text = text
        self.creationTimeUTC = str(datetime.datetime.utcnow())
        self.hidden = False

    def __str__(self):
        return(f"\townerUUID: {self.ownerUUID}\n\tsubject: {self.subject}\n\ttext: {self.text}\n\tcreationTimeUTC: {self.creationTimeUTC}\n")


def AddNote(user: accounts.Account, subject: str, text: str) -> bool:
    subjectInUse = next((x for x in Notes if ((x.ownerUUID == user.uuid) and (x.subject.lower() == subject.lower()))), None)
    if (subjectInUse): raise ValueError("Subject name already in use!")

    newNote = Note(user.uuid,subject,text)
    Notes.append(newNote)

    try:
        UpdateNotes(True)
    except:
        Notes.remove(newNote)
        pass


def UpdateNotes(append: bool = False) -> None:

    jsonData = json.dumps([item.__dict__ for item in Notes], cls=UUIDEncoder, indent=4)

    mode = 'r+' if append else 'w'
    with open('notes.json', mode) as outfile: outfile.write(jsonData)



def RemoveNote(user: accounts.Account, subject: str) -> None:
    noteToDelete = next((x for x in Notes if ((x.ownerUUID == user.uuid) and (x.subject.lower() == subject.lower()))), None)
    if (noteToDelete is None): raise ValueError("No note found with this subject to be deleted!")

    Notes.remove(noteToDelete)
    UpdateNotes()


def RemoveAllNotes() -> None:
    if os.stat("notes.json").st_size == 0: return

    open('notes.json', 'w').close()
    global Notes
    Notes = []


def RestoreNotes() -> None:

    if not os.path.isfile("notes.json"): open('notes.json', 'w').close()

    if os.stat("notes.json").st_size == 0: return
    with open('notes.json', 'r') as data: notes = json.load(data)

    global Notes
    for note in notes:
        loadedNote = Note(uuid.UUID(note['ownerUUID']),note['subject'],note['text'])
        loadedNote.creationTimeUTC = note['creationTimeUTC']

        Notes.append(loadedNote)