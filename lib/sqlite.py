import datetime
import sqlite3
import uuid

import lib.accounts as accounts
import lib.notes as notes


sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

Conn = sqlite3.connect("notes.db", detect_types=sqlite3.PARSE_DECLTYPES)

def Init():
    try:
        cur = Conn.cursor()

        # Create accounts table
        cur.execute("""CREATE TABLE IF NOT EXISTS accounts (     
                    uuid GUID PRIMARY KEY,
                    name TEXT NOT NULL,
                    salt INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        
        # Create Notes Table
        cur.execute("""CREATE TABLE IF NOT EXISTS notes (
                    owner TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    text TEXT,
                    creationTimeUTC DATE NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        

    except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)



# ACCOUNTS
def InsertAccount(account):
    # TODO Make sure account uuid is already not added (USE PRIMARY KEY)
    cur = Conn.cursor()
    import uuid
    uuid = uuid.UUID(bytes(account.uuid))
    print(uuid)
    cur.execute("INSERT INTO accounts (uuid,name,salt,email,password,hidden) VALUES (?,?,?,?,?,?)",(uuid.uuid4(), account.name, account.salt, account.email, account.password, account.hidden))

def UpdateAccount(account):
    cur = Conn.cursor()
    cur.execute("UPDATE accounts SET name = ?, email = ?, password = ?, hidden = ? WHERE uuid = ?",(account.name, account.email, account.password, account.hidden, account.uuid))

def RemoveAccount(account):
    cur = Conn.cursor()
    cur.execute("DELETE FROM accounts WHERE uuid = ?", (account.uuid))

def LoadAccount(uuid: str):
    cur = Conn.cursor()
    print("asd")
    cur.execute("SELECT * FROM accounts WHERE uuid = ?", (uuid))
    print("asd")
    results = cur.fetchall()
    print("asd")
    for row in results:
        print(row)



# NOTES
def InsertNote(note):
    cur = Conn.cursor()
    cur.execute("INSERT INTO notes (owner,subject,text,creationTimeUTC,hidden) VALUES (?,?,?,?,?)",(note.ownerUUID, note.subject, note.text, note.creationTimeUTC, note.hidden))

def UpdateNote(note):
    cur = Conn.cursor()
    cur.execute("UPDATE notes SET subject = ?, text = ?, hidden = ?, WHERE owner = ? AND subject = ?",(note.subject, note.text, note.hidden, note.ownerUUID, note.subject))

def RemoveNote(note): # DONT USE! (Use update with hidden=true)
    cur = Conn.cursor()
    cur.execute("DELETE FROM notes WHERE owner = ? AND subject = ?",(note.ownerUUID, note.subject))

def LoadNote(owner: str, subject: str):
    cur = Conn.cursor()
    cur.execute("SELECT * FROM notes WHERE owner = ? AND subject = ?",(owner, subject))