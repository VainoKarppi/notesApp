import datetime
import lib.accounts as accounts

#! ----------------------
#! NOTES FUNCTIONS
#! ----------------------
Notes = []
class Note:
    def __init__(self, ownerUUID: str, subject: str, text: str):
        self.ownerUUID = ownerUUID
        self.subject = subject
        self.text = text
        self.creationTimeUTC = str(datetime.datetime.utcnow())

    def __str__(self):
        return(f"\townerUUID: {self.ownerUUID}\n\tsubject: {self.subject}\n\ttext: {self.text}\n\tcreationTimeUTC: {self.creationTimeUTC}\n")


def AddNote(user: accounts.Account, subject: str, text: str) -> None:
    print(f"Creating new note for user: [({user.name}) - ({user.uuid})] with subject: ({subject})")

    subjectInUse = next((x for x in Notes if ((x.ownerUUID == user.uuid) and (x.subject.lower() == subject.lower()))), None)
    if (subjectInUse): raise ValueError("Subject name already in use!")

    newNote = Note(user.uuid,subject,text)
    Notes.append(newNote)

    UpdateNotes(True)


def UpdateNotes(append: bool = False) -> None:
    import json

    jsonData = json.dumps([item.__dict__ for item in Notes])

    mode = 'r+' if append else 'w'
    with open('notes.json', mode) as outfile: outfile.write(jsonData)


def RemoveNote(user: accounts.Accounts, subject: str) -> None:
    print(f"Removing a note from user: [({user.name}) - ({user.uuid})] with subject: {subject}")
    noteToDelete = next((x for x in Notes if ((x.ownerUUID == user.uuid) and (x.subject.lower() == subject.lower()))), None)
    if (noteToDelete is None): raise ValueError("No note found with this subject to be deleted!")

    Notes.remove(noteToDelete)
    UpdateNotes()


def RemoveNotes() -> None:
    print("Clearing all saved notes...")

    import os
    if os.stat("notes.json").st_size == 0: return

    open('notes.json', 'w').close()
    global Notes
    Notes = []


def RestoreNotes() -> None:
    print("Restoring notes...")

    import json
    import os

    if not os.path.isfile("notes.json"): open('notes.json', 'w').close()

    if os.stat("notes.json").st_size == 0: return
    with open('notes.json', 'r') as data: notes = json.load(data)

    global Notes
    for note in notes:
        loadedNote = Note(note['ownerUUID'],note['subject'],note['text'])
        loadedNote.creationTimeUTC = note['creationTimeUTC']

        Notes.append(loadedNote)

    print(f"Restored {len(Notes)} notes(s)...\n")