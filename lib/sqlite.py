import datetime
import sqlite3

import lib.accounts as accounts
import lib.notes as notes

Conn = sqlite3.connect("notes.db")

def Init():
    try:
        cur = Conn.cursor()

        # Create accounts table
        cur.execute("""CREATE TABLE IF NOT EXISTS accounts (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    salt INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        
        # Create Notes Table
        cur.execute("""CREATE TABLE notes (
                    owner TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    text TEXT,
                    creationTimeUTC DATE NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        


    except:
        print("ERROR")



# ACCOUNTS
def InsertAccount(account):
    import uuid
    cur = Conn.cursor()
    cur.execute("INSERT INTO accounts (uuid,name,salt,email,password,hidden) VALUES (?,?,?,?,?,?)",(account.uuid, account.name, account.salt, account.email, account.password, account.hidden))

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