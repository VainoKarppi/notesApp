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
```

# Usage
Anyone can see, create or delete new users but only logged users can see their notes.<br/>
By default there is a admin user that can be used to test stuff:
```
Username: admin
password: admin
```
Email can be also used to login instead of username.<br/>
All passwords are hashed using MD5 and simple salt number.

### <u>Commands</u>
<u>*In all modes **Help** command can be used to view the currently available commands and descriptions.*</u>
<br/>

**Account Mode**<br/>
Account mode is the mode that can be used to create, view or remove accounts. This mode is the first mode to open when starting the applciation.<br/><br/>
<u>Available commands in Account Mode:</u>
```
Notes           - (Enter Notes Mode)
Login           - (Login to account)
Logout          - (Logout from the current account)
AddAccount      - (Create Account)
RemoveAccount   - (Remove Account)
ViewAccount     - (Shows current account info)
ShowAccounts    - (Show All Accounts)
Exit            - (Closes Program)
```

**Notes Mode**<br/>
This mode is used to create, view or remove notes that are assigned to current user. To be able to enter this mode a user must first login using the **Login** command, and after that by using the **Notes** command.<br/><br/>
<u>Available commands in Notes Mode:</u>
```
Help            - (Show this help page)
AddNote         - (Create new note)
RemoveNote      - (Removes a note)
EditNote        - (Edit Existing Note)
ShowNotes       - (Show All Available Notes)
ReadNote        - (View a Specific Note)
SearchNote      - (Search for a Note)
Exit            - (Return to Account Mode)
```

# Features
A simple login and logout system. This is a modular system that can be moved to another projects later on. It uses a MD5 hash for passwords with salt number between 100000 and 999999.

A Note system where the notes are all saved in the same file but are fetched by using the owners uuid.

# Contributing
