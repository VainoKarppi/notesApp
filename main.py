
import datetime

import lib.notes as notes
import lib.accounts as accounts
import lib.sqlite as sqlite




#! --------------------
#! OTHER FUNCTIONS
#! --------------------

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
        print(f"\nHelp  - (Show this help page)")
        print(f"Notes - (Enter Notes Mode)")
        print(f"Login - (Login to account)")
        print(f"Logout - (Logout from the current account)")
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
        print(f"ShowNotes - (Show All Available Notes)")
        print(f"ReadNote - (View a Specific Note)")
        print(f"SearchNote - (Search for a Note)")
        print(f"Exit - (Return to Account Mode)")



if __name__=='__main__':
    import os; os.system('cls' if os.name == 'nt' else 'clear')
    print("STARTING PROGRAM...\n")
    
    sqlite.Init()

    #accounts.RestoreAccounts()
    #notes.RestoreNotes()
    accounts.RemoveAccounts()
    
    admin = None

    if (len(accounts.Accounts) == 0):
        admin = accounts.AddAccount("admin","admin","admin@mail.com")

    if (admin is not None):
        sqlite.InsertAccount(admin)

    print("Type 'help' to view commands!")
    loggedUser = None
    while 1==1:
        try:
            #* ACCOUNT MODE
            if UiMode == 1:
                command = input("\n[*ACCOUNT MODE*]: Enter command:\n> ").lower()

                # Make sure session is still valid
                if (loggedUser is not None and accounts.IsUserSessionValid(loggedUser.uuid) == False): loggedUser = None; print("Logged out! Session invalid"); continue

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
                    loggedUser = accounts.Login(username,password)
                    sqlite.LoadAccount(loggedUser.uuid)
                
                if (command == "logout"):
                    if (loggedUser is None): continue
                    loggedUser = None
                    print(f"User [{loggedUser.name}- ({loggedUser.uuid})] Logged Out!")

                if (command == "addaccount"): 
                    username = input("Enter username:\n> ")
                    password = input("Enter password:\n> ")
                    email = input("Enter email:\n> ")
                    accounts.AddAccount(username,password,email)

                if (command == "removeaccount"):
                    uuid = input("Enter user email or uuid\n> ")
                    accounts.RemoveAccount(uuid)

                if (command == "viewaccount"):
                    if (loggedUser is None):
                        print("Not logged in!")
                    else:
                        print(loggedUser)

                if (command == "showaccounts"):
                    index = 0
                    for account in accounts.Accounts:
                        index = index + 1
                        print(f"ACCOUNT: ({index})")
                        print(account)

                if (command == "exit"): break

            #* NOTE EDIT MODE
            elif UiMode == 2:
                command = input("\n[*NOTES MODE*]: Enter command:\n> ").lower()

                if ((loggedUser is None) or (accounts.IsUserSessionValid(loggedUser.uuid) == False)):
                    import os; os.system('cls' if os.name == 'nt' else 'clear')
                    print("NOTES Mode Session Terminated! (invalid session)")
                    UiMode = 1
                    continue

                if (command == "help"): CommandsHelp()
                    
                if (command == "shownotes"):
                    thisUsersNotes = [x for x in notes.Notes if x.ownerUUID == loggedUser.uuid]
                    if (len(thisUsersNotes) == 0): print("No notes found for current user!")
                    
                    index = 0
                    for note in thisUsersNotes:
                        index = index + 1
                        print(f"NOTE: ({index})")
                        print(note)

                if (command == "addnote"):
                    subject = input("Enter subject name:\n> ")
                    text = input("Enter text:\n> ")
                    notes.AddNote(loggedUser,subject,text)

                if (command == "removenote"):
                    subject = input("Enter subject name of the note you want to delete:\n> ")
                    notes.RemoveNotes(loggedUser,subject)

                if (command == "editnote"):
                    subject = input("Enter subject name to edit:\n> ")
                    # Uses memory address reference for the list item
                    note = next((x for x in notes.Notes if x.subject.lower() == subject.lower()), None)
                    if (note is None): print("No note was found with this subject name!"); continue
                    note.text = input("Enter new text for the note\n> ")
                    notes.UpdateNotes()

                if (command == "readnote"):
                    subject = input("Enter subject name to read:\n> ")
                    note = next((x for x in notes.Notes if x.subject.lower() == subject.lower()), None)
                    if (note is None): print("No note was found with this subject name!"); continue
                    print(f"\n(Subject: {note.subject})\nText:\t{note.text}")

                if (command == "searchnote"):
                    searchMode = input("Enter number what to search with:\n\t1) Subject\n\t2) Date\n\t3) Text\n> ")
                    if (searchMode == "1"):
                        subjectFilter = input("\nEnter subject filter:\n> ")
                        notes = [x for x in notes.Notes if (x.ownerUUID == loggedUser.uuid and subjectFilter.lower() in x.subject.lower())]
                        print(f"Found {len(notes)} note(s) with this subject filter!")
                        for note in notes: print(note)

                    #TODO add hours and minutes support
                    elif (searchMode == "2"):
                        startDateText = input("\nEnter start date for filter (dd/mm/yyyy):\n> ")
                        startDate = datetime.datetime(int(startDateText.split('/')[2]), int(startDateText.split('/')[1]), int(startDateText.split('/')[0]))

                        endDateText = input("\nEnter end date for filter (dd/mm/yyyy) - (leave empty for today):\n> ")
                        endDate = datetime.datetime.utcnow()
                        if (len(endDateText) != 0):
                            endDate = datetime.datetime(int(endDateText.split('/')[2]), int(endDateText.split('/')[1]), int(endDateText.split('/')[0]))
                            
                        notes = [x for x in notes.Notes if (x.ownerUUID == loggedUser.uuid and (startDate < ParseStringToDate(x.creationTimeUTC) < endDate))]
                        print(f"Found {len(notes)} note(s) with these date filters!")
                        for note in notes: print(note)

                    elif (searchMode == "3"):
                        textFilter = input("\nEnter text filter:\n> ")
                        notes = [x for x in notes.Notes if (x.ownerUUID == loggedUser.uuid and textFilter.lower() in x.text.lower())]
                        print(f"Found {len(notes)} note(s) with this subject filter!")
                        for note in notes: print(note)

                if (command == "exit"):
                    import os; os.system('cls' if os.name == 'nt' else 'clear')
                    UiMode = 1

        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)

    #! DEBUG COMMANDS
    #Reset accounts!
    #RemoveAccounts()

    #Reset notes!
    #RemoveNotes()

    print("\nBYE! 👋\n")

    import sys; sys.exit(0)