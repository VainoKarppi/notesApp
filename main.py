import datetime

#! ----------------------
#! ACCOUNTS METHODS
#! ----------------------
Accounts = []
class Account:
    def __init__(self, name, password, email, uuid = None, salt = None):
        from uuid import uuid4
        from random import randint
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.name = name
        self.salt = str(randint(1000000,9999999)) if salt is None else salt
        self.email = email
        self.password = password if IsMD5hash(password) else ComputeMD5hash(password,self.salt)
    
    def __str__(self):
        return(f"\tuuid: {self.uuid}\n\tname: {self.name}\n\tpassword: {self.password}\n\temail: {self.email}\n\tsalt: {self.salt}\n")



def Login(usernameOrEmail: str, password: str) -> Account:
    isEmail = '@' in usernameOrEmail
    fetchedAccounts = []
    if isEmail:
        fetchedAccounts = [x for x in Accounts if x.email.lower() == usernameOrEmail.lower()]
    else:
        fetchedAccounts = [x for x in Accounts if x.name == usernameOrEmail]
    for account in fetchedAccounts:
        #TODO what if there is a username and same password is use for two accounts?? (Ask for email) 😬
        hashedPassword = ComputeMD5hash(password,account.salt)
        if hashedPassword == account.password:
            print(f"Account: [({account.name}) | ({account.uuid})] Logged in!")   
            return account
        
    print(f"Invalid username or password! ({usernameOrEmail})")
    return None

# Returns True if successfully removed. False if not
def RemoveAccount(uuidOrEmail) -> bool:
    print(f"Removing account... ({uuidOrEmail})")

    account = None
    isEmail = '@' in uuidOrEmail
    if isEmail:
        account = next((x for x in Accounts if x.email.lower() == uuidOrEmail.lower()), None)
    else:
        account = next((x for x in Accounts if x.uuid == uuidOrEmail), None)

    if account is None:
        print("Cannot find user with this uuid or email!")
        return False
    
    Accounts.remove(account)
    UpdateAccounts()

    return True


# Returns create Account class
def AddAccount(name, password, email) -> Account:
    print(f"Creating account... ({name}) - ({email})\n")

    if '@' in name:
        print("Username cannot be email!")
        return None
    if '@' not in email:
        print("Invalid Email!")
        return None

    emailInUse = next((x for x in Accounts if x.email.lower() == email.lower()), None) != None
    if (emailInUse):
        print("Email already in use!")
        return None
    
    account = Account(name,password,email)
    Accounts.append(account)
    
    UpdateAccounts()

    return account

def UpdateAccounts() -> None:
    import json
    jsonData = json.dumps([item.__dict__ for item in Accounts])

    # Overwrite ALL instead of add single
    with open('accounts.json', 'r+') as outfile:
        outfile.write(jsonData)
        outfile.close()


def RemoveAccounts() -> None:
    print("Clearing all saved accounts...")

    import os
    if os.stat("accounts.json").st_size == 0: return

    
    open('accounts.json', 'w').close()
    global Accounts
    Accounts = []


def RestoreAccounts() -> None:
    print("Restoring accounts...")

    import json
    import os

    if os.stat("accounts.json").st_size == 0: return
    with open('accounts.json', 'r') as data:
        accounts = json.load(data)

    global Accounts
    for account in accounts:
        loadedAccount = Account(account['name'],account['password'],account['email'],account['uuid'],account['salt'])
        Accounts.append(loadedAccount)

    print(f"Restored {len(Accounts)} account(s)...\n")


def UserSessionValid(uuid: str) -> bool:
    found = next((x for x in Accounts if x.uuid == uuid), None) != None
    return found


def ComputeMD5hash(password: str, salt: str) -> str:
    import hashlib
    result = hashlib.md5((password + salt).encode())
    return (result.hexdigest())


def IsMD5hash(password: str) -> bool:
    import re
    return bool(re.match(r"^[a-fA-F0-9]{32}$", password))













#! ----------------------
#! NOTES METHODS
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


def AddNote(user: Account, subject: str, text: str) -> bool:
    print(f"Creating new note for user: [({user.name}) - ({user.uuid})] with subject: ({subject})")

    subjectInUse = next((x for x in Notes if ((x.ownerUUID == user.uuid) and (x.subject.lower() == subject.lower()))), None)
    if (subjectInUse):
        print("Subject name already in use!")
        return False

    newNote = Note(user.uuid,subject,text)
    Notes.append(newNote)

    UpdateNotes()
    return True


def UpdateNotes() -> None:
    import json

    jsonData = json.dumps([item.__dict__ for item in Notes])

    # Overwrite ALL instead of add single
    with open('notes.json', 'r+') as outfile:
        outfile.write(jsonData)
        outfile.close()


def RemoveNote(user: Account, subject: str) -> bool:
    print(f"Removing a note from user: [({user.name}) - ({user.uuid})] with subject: {subject}")
    noteToDelete = next((x for x in Notes if ((x.ownerUUID == user.uuid) and (x.subject.lower() == subject.lower()))), None)
    if (noteToDelete is None):
        print("No note found with this subject to be deleted!")
        return False

    Notes.remove(noteToDelete)
    UpdateNotes()

    return True


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

    if os.stat("notes.json").st_size == 0: return
    with open('notes.json', 'r') as data:
        notes = json.load(data)

    global Notes
    for note in notes:
        loadedNote = Note(note['ownerUUID'],note['subject'],note['text'])
        loadedNote.creationTimeUTC = note['creationTimeUTC']

        Notes.append(loadedNote)

    print(f"Restored {len(Notes)} notes(s)...\n")




# can be parsed from datetime.datetime.utcnow()
def ParseStringToDate(dateString: str) -> datetime:
    date = datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S.%f")
    return date











#! --------------------
#! USER INTERFACE
#! --------------------
UiMode = 1
def CommandsHelp():
    if UiMode == 1:
        print(f"\nHelp - (Show this help page)")
        print(f"Notes - (Enter Notes Mode)")
        print(f"Login - (Login to account)")
        print(f"Logout - (Login to account)")
        print(f"AddAccount - (Create Account)")
        print(f"RemoveAccount - (Remove Account)")
        print(f"ViewAccount - (Shows current account info)")
        print(f"ShowAccounts - (Show All Accounts)")
        print(f"Exit - (Closes Program)\n")
    elif UiMode == 2:
        print(f"\nHelp - (Show this help page)")
        print(f"AddNote - (Create new note)")
        print(f"RemoveNote - (Removes a note)")
        print(f"EditNote - (Edit Existing Note)")
        print(f"ShowNotes - (View Existing Note)")
        print(f"ReadNote - (View Existing Note)")
        print(f"SearchNote - (View Existing Note)")
        print(f"Exit - (Return to Account Mode)")



if __name__=='__main__':
    import os; os.system('cls' if os.name == 'nt' else 'clear')
    print("STARTING PROGRAM...\n")
    RestoreAccounts()
    RestoreNotes()

    if (len(Accounts) == 0):
        AddAccount("admin","admin","admin@gmail.com")

    print("Type 'help' to view commands!")
    loggedUser = None
    while 1==1:
        if UiMode == 1:
            command = input("\n[*ACCOUNT MODE*] > Enter command:\n> ").lower()

            # Make sure session is still valid
            if (loggedUser is not None and UserSessionValid(loggedUser.uuid) == False): loggedUser = None; continue

            if (command == "help"): CommandsHelp()
            if (command == "notes"):
                if (loggedUser is None):
                    print("You need to login first!")
                else:
                    UiMode = 2
                    print("Entered In Notes Mode!")
                    import os; os.system('cls' if os.name == 'nt' else 'clear')
                    
            if (command == "login"):
                if (loggedUser is not None): print("Already logged in!"); continue

                username = input("Enter username or email:\n> ")
                password = input("Enter password:\n> ")
                loggedUser = Login(username,password)
            
            if (command == "logout"):
                if (loggedUser is None): continue
                loggedUser = None
                print(f"User [{loggedUser.name}- ({loggedUser.uuid})] Logged Out!")

            if (command == "addaccount"): 
                username = input("Enter username:\n> ")
                password = input("Enter password:\n> ")
                email = input("Enter email:\n> ")
                AddAccount(username,password,email)

            if (command == "removeaccount"):
                uuid = input("Enter user email or uuid\n> ")
                RemoveAccount(uuid)

            if (command == "viewaccount"):
                if (loggedUser is None):
                    print("Not logged in!")
                else:
                    print(loggedUser)

            if (command == "showaccounts"):
                index = 0
                for account in Accounts:
                    index = index + 1
                    print(f"ACCOUNT: ({index})")
                    print(account)

            if (command == "exit"): break

        #! NOTE EDIT MODE
        elif UiMode == 2:
            command = input("\n[*NOTES MODE*] > Enter command:\n> ").lower()

            if ((loggedUser is None) or (UserSessionValid(loggedUser.uuid) == False)):
                import os; os.system('cls' if os.name == 'nt' else 'clear')
                print("NOTES Mode Session Terminated! (invalid session)")
                UiMode = 1
                continue

            if (command == "help"): CommandsHelp()
                
            if (command == "shownotes"):
                thisUsersNotes = [x for x in Notes if x.ownerUUID == loggedUser.uuid]
                index = 0
                for note in thisUsersNotes:
                    index = index + 1
                    print(f"NOTE: ({index})")
                    print(note)

            if (command == "addnote"):
                subject = input("Enter subject name:\n> ")
                text = input("Enter text:\n> ")
                AddNote(loggedUser,subject,text)

            if (command == "removenote"):
                subject = input("Enter subject name of the note you want to delete:\n> ")
                RemoveNote(loggedUser,subject)

            if (command == "editnote"):
                subject = input("Enter subject name to edit:\n> ")
                # Uses memory address reference for the list item
                note = next((x for x in Notes if x.subject.lower() == subject.lower()), None)
                if (note is None): print("No note was found with this subject name!"); continue
                note.text = input("Enter new text for the note\n> ")
                UpdateNotes()

            if (command == "readnote"):
                subject = input("Enter subject name to read:\n> ")
                note = next((x for x in Notes if x.subject.lower() == subject.lower()), None)
                if (note is None): print("No note was found with this subject name!"); continue
                print(f"\n(Subject: {note.subject})\nText:\t{note.text}")

            if (command == "searchnote"):
                mode = input("Enter number what to search with:\n\t1) Subject\n\t2) Date\n\t3) Text\n> ")
                if (mode == "1"):
                    subjectFilter = input("\nEnter subject filter:\n> ")
                    notes = [x for x in Notes if (x.ownerUUID == loggedUser.uuid and subjectFilter.lower() in x.subject.lower())]
                    print(f"Found {len(notes)} note(s) with this subject filter!")
                    for note in notes: print(note)

                #TODO add hours and minutes support
                elif (mode == "2"):
                    startDateText = input("\nEnter start date for filter (dd/mm/yyyy):\n> ")
                    startDate = datetime.datetime(int(startDateText.split('/')[2]), int(startDateText.split('/')[1]), int(startDateText.split('/')[0]))

                    endDateText = input("\nEnter end date for filter (dd/mm/yyyy) - (leave empty for today):\n> ")
                    endDate = datetime.datetime.utcnow()
                    if (len(endDateText) != 0):
                        endDate = datetime.datetime(int(endDateText.split('/')[2]), int(endDateText.split('/')[1]), int(endDateText.split('/')[0]))
                        
                    notes = [x for x in Notes if (x.ownerUUID == loggedUser.uuid and (startDate < ParseStringToDate(x.creationTimeUTC) < endDate))]
                    print(f"Found {len(notes)} note(s) with these date filters!")
                    for note in notes: print(note)

                elif (mode == "3"):
                    textFilter = input("\nEnter text filter:\n> ")
                    notes = [x for x in Notes if (x.ownerUUID == loggedUser.uuid and textFilter.lower() in x.text.lower())]
                    print(f"Found {len(notes)} note(s) with this subject filter!")
                    for note in notes: print(note)

            if (command == "exit"):
                import os; os.system('cls' if os.name == 'nt' else 'clear')
                UiMode = 1

    #Reset accounts!
    #RemoveAccounts()

    #Reset notes!
    #RemoveNotes()

    print("\nBYE! 👋\n")