
from datetime import datetime
import os

import lib.notes as notes
import lib.accounts as accounts
import lib.sqlitedb as db
import lib.webserver as webserver

Debug = False


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
        print(f"CreateAccount - (Creates a new account)")
        print(f"Exit - (Closes Program)")
    elif UiMode == 2:
        print(f"Notes - (Enter Notes Mode)")
        print(f"Logout - (Logout from the current account)")
        print(f"ChangePassword - (Updates current users password)")
        print(f"ViewAccount - (Shows current account info)")
        print(f"RemoveAccount - (Remove Account)")
        if LoggedUser is not None and LoggedUser.admin:
            print(f"\n[ ADMIN COMMANDS ]")
            print(f"CreateAccount - (Create Account)")
            print(f"ShowAccounts - (Show All Accounts)")
            print(f"RemoveOtherAccount - (Remove Someone Else's Account)")

    elif UiMode == 3:
        print(f"Help - (Show this help page)")
        print(f"AddNote - (Create new note)")
        print(f"RemoveNote - (Removes a note)")
        print(f"EditNote - (Edit Existing Note)")
        print(f"ImportNote - (Import a note from a file)")
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
    print("Stopping WEB server...")
    webserver.StopServer()


    if (db.ConnectionOpen()):
        print("Stopping database...")
        db.Cursor.close()
        db.Conn.commit()
        db.Conn.close()

    print("\nBYE! 👋\n")
    import sys; sys.exit(code)



try:
    if __name__=='__main__':
        os.system('cls' if os.name == 'nt' else 'clear')
        
        #db.Conn.execute("DROP TABLE IF EXISTS accounts")
        #db.Conn.execute("DROP TABLE IF EXISTS notes")
        
        db.Init()
        webserver.StartServer("127.0.0.1",8000)
        print("You can also access the notes using your browser at:\n\t- http://127.0.0.1:8000/notes\n\t- http://127.0.0.1:8000/note?subject=NOTESUBJECTHERE\n")

        
        if (db.EmailInUse("admin@mail.com") == False):
            print("Creating Admin account: (username: admin | password: admin)")
            admin = accounts.CreateAccount("admin","admin","admin@mail.com",True)


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
                    
                    if (command == "createaccount"):
                        username = input("\nEnter username:\n> ")
                        if (len(username) < 5): raise ValueError("Username must be at least 5 characters")
                        password = input("\nEnter password:\n> ")
                        if (len(password) < 5): raise ValueError("Password must be at least 5 characters")
                        email = input("\nEnter email:\n> ")
                        print(f"Creating account... ({username}) - ({email}) - Admin:{False}\n")

                        newAccount = accounts.CreateAccount(username,password,email,False)
                        if (newAccount is None): raise Exception("Account creation failed!")
                        print("Account created succesfully!")


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
                            newPassword = input("\nEnter NEW password:\n> ")
                            accounts.UpdatePassword(LoggedUser,newPassword)


                    # Remove this account
                    if (command == "removeaccount"):
                        result = input("\nAre you sure you want to remove your account? (yes/no)\n> ")
                        if (result.lower() == "true" or result.lower() == "yes" or result.lower() == "1"):
                            accounts.RemoveAccount(LoggedUser.email)
                            LoggedUser = None
                            UiMode = 1
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print("Account removed succesfully!")
                            continue # Dont continue since LoggedUser.admin is used later

                    #* ADMIN COMMANDS
                    if (LoggedUser.admin):
                        if (command == "createaccount"): 
                            username = input("\nEnter username:\n> ")
                            if (len(username) < 5): raise ValueError("Username must be at least 5 characters")
                            password = input("\nEnter password:\n> ")
                            if (len(password) < 5): raise ValueError("Password must be at least 5 characters")
                            email = input("\nEnter email:\n> ")
                            admin = input("\nIs admin (yes/no):\n> ")
                            isAdmin = admin.lower() == "true" or admin == "1" or admin.lower() == "yes"
                            print(f"Creating account... ({username}) - ({email}) - Admin:{isAdmin}\n")
                            newAccount = accounts.CreateAccount(username,password,email,isAdmin)
                            if (newAccount is None): raise Exception("Account creation failed!")
                            print("Account created succesfully!")

                        if (command == "showaccounts"):
                            index = 0
                            for account in accounts.GetAllAccounts():
                                index = index + 1
                                print(f"ACCOUNT: ({index})")
                                print(account)

                        if (command == "removeotheraccount"):
                            data = input("\nEnter user email or uuid\n> ")
                            accounts.RemoveAccount(data)
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
                        allNotes = notes.GetAllUserNotes(LoggedUser.uuid)
                        if (len(allNotes) == 0): print("No notes found for current user!")
                        index = 0
                        for note in allNotes:
                            index = index + 1
                            if (note is not None):
                                print(f"NOTE: ({index})")
                                print(note)


                    if (command == "addnote"):
                        subject = input("\nEnter subject name:\n> ")
                        text = input("\nEnter text:\n> ")
                        www = input("\nEnter www path:\n> ")
                        note = notes.CreateNote(LoggedUser,subject,text,www)
                        if (note is None): raise Exception("Note creation failed!")
                        print("Note added succesfully!")

                    if (command == "removenote"):
                        subject = input("\nEnter subject name of the note you want to delete:\n> ")
                        notes.RemoveNote(LoggedUser.uuid,subject)
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

                        notes.RemoveAllUserNotes(user.uuid)

                    if (command == "editnote"):
                        subject = input("\nEnter subject name to edit:\n> ")
                        note = notes.GetNote(LoggedUser.uuid,subject)
                        if (note is None): raise ValueError("No note was found with this subject name!")
                        
                        note.text = input("\nEnter new text for the note\n> ")
                        notes.UpdateNote(note)

                        print("Note Updated Succesfully")


                    if (command == "readnote"):
                        subject = input("\nEnter subject name to read:\n> ")
                        note = notes.GetNote(LoggedUser.uuid,subject)
                        if (note is None): raise ValueError("No note was found with this subject name!")
                        print(f"\n(Subject: {note.subject})\nText:\t{note.text}")

                    if (command == "searchnote"):
                        searchMode = input("\nEnter number what to search with:\n\t1) Subject\n\t2) Date\n\t3) Text\n> ")
                        if (searchMode == "1"):
                            subjectFilter = input("\nEnter subject filter:\n> ")
                            foundNotes = notes.FindNotes(LoggedUser.uuid,subjectFilter,"subject")
                            print(f"Found {len(foundNotes)} note(s) with this subject filter!")
                            for note in foundNotes: print(note)

                        #TODO add hours and minutes support
                        elif (searchMode == "2"):
                            allNotes = notes.GetAllUserNotes(LoggedUser.uuid)
                                
                            startDateText = input("\nEnter start date for filter in UTC (dd/mm/yyyy):\n> ")
                            startDate = datetime(int(startDateText.split('/')[2]), int(startDateText.split('/')[1]), int(startDateText.split('/')[0]))

                            endDateText = input("\nEnter end date for filter in UTC (dd/mm/yyyy) - (leave empty for today):\n> ")
                            endDate = datetime.utcnow()
                            if (len(endDateText) != 0):
                                endDate = datetime(int(endDateText.split('/')[2]), int(endDateText.split('/')[1]), int(endDateText.split('/')[0]))
                                
                            foundNotes = [x for x in allNotes if (startDate < x.creationTimeUTC < endDate)]
                            print(f"Found {len(foundNotes)} note(s) with these date filters!")
                            for note in foundNotes: print(note)

                        elif (searchMode == "3"):
                            textFilter = input("\nEnter text filter:\n> ")
                            foundNotes = notes.FindNotes(LoggedUser.uuid,textFilter,"text")
                            print(f"Found {len(foundNotes)} note(s) with this text filter!")
                            for note in foundNotes: print(note)
                    
                    if (command == "importnote"):
                        path = input("\nEnter path of the file:\n> ")
                        notes.ImportNoteFile(LoggedUser.uuid,path)
                        print("Note imported succesfully!")

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