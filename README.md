# VainoKarppi/NotesApp

A Simple CLI Note app that stores notes with authentication. Currently the data is stored in two json files: ***accounts.json*** and ***notes.json***, but later this will be moved to **MySQL**!

**THIS PROJECT IS CURRENTLY WIP AND PRIVATE!**

# Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)

# Installation

This project is not using any 3rd party libaries. Project contains ***.vscode\launch.json*** file that can be used to launch the project. All functions are stored in the single **main.py** file.

```bash
git clone https://github.com/VainoKarppi/notesApp.git
cd notesApp

python.exe .\main.py

# TO RUN IN DEBUG MODE:
python.exe .\main.py debug
```

# Usage
Anyone can see, create or delete new users but only logged users can see their notes.<br/>
By default there is a admin user that can be used to test stuff:
```
Username: admin
password: admin
```
Email can be also used to login instead of username.<br/>
All passwords are hashed using SHA256 and simple salt number.

### <u>Commands</u>
<u>*In all modes **Help** command can be used to view the currently available commands and descriptions.*</u>
<br/>

**Guest Mode**<br/>
Guest mode is the mode that is currently not in use other than for login and for creating a new account. This mode is the first mode to open when starting the applciation.<br/><br/>
<u>Available commands in Account Mode:</u>
```
Login               - (Login to account)
CreateAccount       - (Create New Account)
Exit                - (Closes Program)
```

**User Mode**<br/>
User mode is the mode that can be used to chanhepassword, view or remove account. For admins there are some extra administrative commands that can be used.
<br/><br/>
<u>Available commands for **NORMAL** User:</u>
```
Notes               - (Enter Notes Mode)
Logout              - (Logout from the current account)
ChangePassword      - (Updates current users password)
RemoveAccount       - (Remove Account)
ViewAccount         - (Shows current account info)
Exit                - (Closes Program)
```
<u>Extra Available commands for **ADMIN** User:</u>
```
CreateAccount       - (Create Account and specify if admin)
ShowAccounts        - (Show All Accounts)
RemoveOtherAccount  - (Remove Someone Else's Account)
```

**Notes Mode**<br/>
This mode is used to create, view or remove notes that are assigned to current user. To be able to enter this mode a user must first login using the **Login** command, and after that by using the **Notes** command.<br/><br/>
<u>Available commands in Notes Mode:</u>
```
AddNote             - (Create new note)
RemoveNote          - (Removes a note)
EditNote            - (Edit Existing Note)
ImportNote          - (Import a note from a file)
ShowNotes           - (Show All User Notes)
RemoveAllNotes      - (Removes all notes from user)
ReadNote            - (View a Specific Note(s))
SearchNote          - (Search for a Note)
```

# Features
A simple login and logout system. This is a modular system that can be moved to another projects later on. It uses a SHA256 hash for passwords with salt number between 100000 and 999999.

A Note system where the notes are all saved in the same file but are fetched by using the owners uuid.

Additional web server that can be used to fetch user notes or a specific note after login.
<br>
Default path: http://localhost:8000/notes
<br>
To query specific note: http://localhost:8000/note?subject=ENTERSUBJECTHERE

**Work In Progress:**
```
TODO: Add Ability to manage notes using HTTP requests.
TODO: HTTPS with secret
```
