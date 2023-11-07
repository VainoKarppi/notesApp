
import datetime
import os;

import lib.notes as notes
import lib.accounts as accounts
import lib.sqlitedb as db

Debug = False


#! --------------------
#! OTHER FUNCTIONS
#! --------------------

# can be parsed from datetime.datetime.utcnow()
def ParseStringToDate(dateString: str) -> datetime:
    date = datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S.%f")
    return date






LoggedUser:accounts.Account = None



#! --------------------
#! USER INTERFACE
#! --------------------
UiMode = 1
def CommandsHelp():
    print("\n===============| HELP COMMANDS |===============")
    if UiMode == 1:
        print(f"Help  - (Show this help page)")
        print(f"Login - (Login to account)")    
        print(f"Exit - (Closes Program)")
    elif UiMode == 2:
        print(f"Notes - (Enter Notes Mode)")
        print(f"Logout - (Logout from the current account)")
        print(f"ChangePassword - (Updates current users password)")
        print(f"ViewAccount - (Shows current account info)")
        print(f"RemoveAccount - (Remove Account)")
        if LoggedUser is not None and LoggedUser.admin:
            print(f"\n[ ADMIN COMMANDS ]")
            print(f"AddAccount - (Create Account)")
            print(f"ShowAccounts - (Show All Accounts)")
            print(f"RemoveAccount - (Remove Account)")

    elif UiMode == 3:
        print(f"Help - (Show this help page)")
        print(f"AddNote - (Create new note)")
        print(f"RemoveNote - (Removes a note)")
        print(f"EditNote - (Edit Existing Note)")
        print(f"ShowNotes - (Show All Available Notes)")
        print(f"RemoveAllNotes - (Removes all notes from user)")
        print(f"ReadNote - (View a Specific Note)")
        print(f"SearchNote - (Search for a Note)")
        print(f"Exit - (Return to Account Mode)")
    
    print("===============================================\n")
    
def Exit(code:int = 0):
    print("\n\n")
    #! DEBUG COMMANDS
    #Reset accounts!
    #RemoveAllAccounts()

    #Reset notes!
    #RemoveAllNotes()

    print("Stopping database...")
    if (db.ConnectionOpen()):
        db.Cursor.close()
        db.Conn.commit()
        db.Conn.close()

    print("\nBYE! 👋\n")
    import sys; sys.exit(code)



try:
    if __name__=='__main__':
        os.system('cls' if os.name == 'nt' else 'clear')
        
        db.Init()

        print("Restoring notes...")
        notes.RestoreNotes()
        print(f"Restored {len([x for x in notes.Notes if (x.hidden == False)])} notes(s)...\n")
        
        if (db.EmailInUse("admin@mail.com") == False):
            print("Creating Admin account: (username: admin | password: admin)")
            admin = accounts.CreateAccount("admin","admin","admin@mail.com",True)
            db.InsertAccount(admin)


        print("Type 'help' to view commands!")
        
        while 1==1:
            try:
                #* GUEST MODE
                if UiMode == 1:
                    LoggedUser = None # Just to make sure in case account gets removed and trown here
                    command = input("\n[*GUEST MODE*]: Enter command:\n> ").lower()

                    if (command == "help"): CommandsHelp()
                    if (command == "exit"): break
                            
                    if (command == "login"):
                        username = input("\nEnter username or email:\n> ")
                        password = input("\nEnter password:\n> ")
                        LoggedUser = accounts.Login(username,password)
                        if (LoggedUser is not None): 
                            UiMode = 2
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(f"Account: [({username}) | ({LoggedUser.uuid})] Logged in!")   
                            continue        
                    



                #* USER LOGGED IN MODE
                elif UiMode == 2:
                    # Make sure session is valid and user is logged in
                    if ((LoggedUser is None) or (accounts.IsUserSessionValid(LoggedUser.uuid) == False)):
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Logged out! (invalid session)")
                        UiMode = 1
                        continue
                    
                    command = input(("\n[*" + ("ADMIN" if LoggedUser.admin else "ACCOUNT") + " MODE*]: Enter command:\n> ")).lower()
                    
                    # Make sure session is STILL valid after input and user is logged in
                    if ((LoggedUser is None) or (accounts.IsUserSessionValid(LoggedUser.uuid) == False)):
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Logged out! (invalid session)")
                        UiMode = 1
                        continue


                    if (command == "help"): CommandsHelp()
                    if (command == "exit"): break

                    # User Logout
                    if (command == "logout"):
                        if (LoggedUser is None): UiMode = 1; continue
                        UiMode = 1
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(f"User [{LoggedUser.name} - ({LoggedUser.uuid})] Logged Out!")
                        LoggedUser = None
                        continue

                    # Enter Notes Mode
                    if (command == "notes"):
                        if (LoggedUser is None):
                            print("You need to login first!")
                        else:
                            UiMode = 3
                            print("Entered In Notes Mode!")
                            os.system('cls' if os.name == 'nt' else 'clear')
                    
                    # View current user info
                    if (command == "viewaccount"):
                        if (LoggedUser is None):
                            print("Not logged in!")
                        else:
                            print(LoggedUser)
                    
                    # Change current user password
                    if (command == "changepassword"):
                        if (LoggedUser is None):
                            print("Not logged in!")
                        else:
                            oldPasswordHash = LoggedUser.password
                            newPassword = input("\nEnter NEW password:\n> ")
                            newPasswordHash = accounts.ComputeSHA3hash(newPassword,LoggedUser.salt)
                            if (newPasswordHash == oldPasswordHash): raise ValueError("NEW Password cannot be same as old password!")

                            LoggedUser.password = newPasswordHash
                            success = db.UpdateAccount(LoggedUser)

                            # Restore old password if update was failed
                            if (success == False): 
                                LoggedUser.password = oldPasswordHash
                                continue
                            
                            print("Password updated succesfully!")


                    #* ADMIN COMMANDS
                    if (LoggedUser.admin):
                        if (command == "addaccount"): 
                            username = input("\nEnter username:\n> ")
                            password = input("\nEnter password:\n> ")
                            email = input("\nEnter email:\n> ")
                            admin = input("\nIs admin (yes/no):\n> ")
                            isAdmin = admin.lower() == "true" or admin == "1" or admin.lower() == "yes"
                            print(f"Creating account... ({username}) - ({email}) - Admin:{isAdmin}\n")
                            newAccount = accounts.CreateAccount(username,password,email,isAdmin)
                            if (newAccount is not None):
                                db.InsertAccount(newAccount)
                                print("Account created succesfully!")

                            else: print("Account creation failed!")

                        if (command == "showaccounts"):
                            index = 0
                            for account in accounts.GetAllAccounts():
                                index = index + 1
                                print(f"ACCOUNT: ({index})")
                                print(account)

                        if (command == "removeaccount"):
                            if (LoggedUser is not None): print(f"Current users uuid: {LoggedUser.uuid}")
                            data = input("\nEnter user email or uuid\n> ")
                            print(f"Removing account... ({data})")
                            accounts.RemoveAccount(data)
                            print("Account removed succesfully!")


                    # Normal user removeaccounta
                    else:
                        if (command == "removeaccount"):
                            result = input("\nAre you sure you want to remove your account? (yes/no)\n> ")
                            if (result.lower() == "true" or result.lower() == "yes" or result.lower() == "1"):
                                deleted = accounts.RemoveAccount(LoggedUser.uuid)
                                if (deleted):
                                    LoggedUser = None
                                    UiMode = 1
                                    print("Account removed succesfully!")


                #* NOTE EDIT MODE
                elif UiMode == 3:
                    command = input("\n[*NOTES MODE*]: Enter command:\n> ").lower()

                    if ((LoggedUser is None) or (accounts.IsUserSessionValid(LoggedUser.uuid) == False)):
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("NOTES Mode Session Terminated! (invalid session)")
                        UiMode = 1
                        continue

                    if (command == "help"): CommandsHelp()
                        
                    if (command == "shownotes"):
                        allNotes = db.LoadAllUserNotes(LoggedUser.uuid)
                        if (len(allNotes) == 0): print("No notes found for current user!")
                        index = 0
                        for note in allNotes:
                            index = index + 1
                            print(f"NOTE: ({index})")
                            print(f"\townerUUID: {note[0]}\n\tsubject: {note[1]}\n\ttext: {note[2]}\n\twebPage: {note[3]}\n\tcreationTimeUTC: {note[4]}\n")


                    if (command == "addnote"):
                        subject = input("\nEnter subject name:\n> ")
                        text = input("\nEnter text:\n> ")
                        print(f"Creating new note for user: [({LoggedUser.name}) - ({LoggedUser.uuid})] with subject: ({subject})")
                        note = notes.CreateNote(LoggedUser,subject,text)
                        db.InsertNote(note)
                        print("Note added succesfully!")

                    if (command == "removenote"):
                        subject = input("\nEnter subject name of the note you want to delete:\n> ")
                        print(f"Removing a note from user: [({LoggedUser.name}) - ({LoggedUser.uuid})] with subject: {subject}")
                        db.RemoveNote(LoggedUser.uuid,subject)
                        print("Note removed succesfully!")
                    
                    if(command == "removeallnotes"):
                        user = LoggedUser
                        if (user.admin):
                            data = input("\nEnter user email or uuid to delete the notes from\n> ")
                            user = accounts.GetAccount(data)
                        
                        if(user is not None):
                            print(f"Removing all notes from user: {user.name}")
                        else:
                            print(f"Removing all notes from user: {data}")
                        notes.RemoveAllNotes(user)

                    if (command == "editnote"):
                        subject = input("\nEnter subject name to edit:\n> ")
                        # Uses memory address reference for the list item
                        note = next((x for x in notes.Notes if x.subject.lower() == subject.lower()), None)
                        if (note is None): print("No note was found with this subject name!"); continue
                        note.text = input("\nEnter new text for the note\n> ")
                        notes.UpdateNotes()

                    if (command == "readnote"):
                        subject = input("\nEnter subject name to read:\n> ")
                        note = next((x for x in notes.Notes if x.subject.lower() == subject.lower()), None)
                        if (note is None): print("No note was found with this subject name!"); continue
                        print(f"\n(Subject: {note.subject})\nText:\t{note.text}")

                    if (command == "searchnote"):
                        searchMode = input("\nEnter number what to search with:\n\t1) Subject\n\t2) Date\n\t3) Text\n> ")
                        if (searchMode == "1"):
                            subjectFilter = input("\nEnter subject filter:\n> ")
                            notes = [x for x in notes.Notes if (x.ownerUUID == LoggedUser.uuid and subjectFilter.lower() in x.subject.lower() and x.hidden == False)]
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
                                
                            notes = [x for x in notes.Notes if (x.ownerUUID == LoggedUser.uuid and (startDate < ParseStringToDate(x.creationTimeUTC) < endDate))]
                            print(f"Found {len(notes)} note(s) with these date filters!")
                            for note in notes: print(note)

                        elif (searchMode == "3"):
                            textFilter = input("\nEnter text filter:\n> ")
                            notes = [x for x in notes.Notes if (x.ownerUUID == LoggedUser.uuid and textFilter.lower() in x.text.lower())]
                            print(f"Found {len(notes)} note(s) with this subject filter!")
                            for note in notes: print(note)

                    if (command == "exit"):
                        os.system('cls' if os.name == 'nt' else 'clear')
                        UiMode = 2


            except Exception as e:
                    if (Debug):
                        import traceback
                        traceback.print_exc()

                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)


# CTRL + C was pressed (KeyboardInterrupt)
except:
    if (Debug):
        import traceback
        traceback.print_exc()

    Exit(0)

Exit(0)