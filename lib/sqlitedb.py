import datetime
import sqlite3
import uuid

import lib.accounts as accounts
import lib.notes as notes


# SUPPORT FOR UUID/GUID FOR DATABASE
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

Conn = sqlite3.connect("notes.db", detect_types=sqlite3.PARSE_DECLTYPES)

def Init():
    try:
        cur = Conn.cursor()

        # Create accounts table
        cur.execute("""CREATE TABLE IF NOT EXISTS accounts (     
                    uuid GUID PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    salt INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        
        # Create Notes Table
        cur.execute("""CREATE TABLE IF NOT EXISTS notes (
                    owner GUID NOT NULL,
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
    cur = Conn.cursor()
    cur.execute("INSERT INTO accounts (uuid,name,salt,email,password,hidden) VALUES (?,?,?,?,?,?)",(uuid.UUID(account.uuid), account.name, account.salt, account.email, account.password, account.hidden))
    Conn.commit()

def UpdateAccount(account):
    cur = Conn.cursor()
    cur.execute("UPDATE accounts SET name=:name, email=:email, password=:password, hidden=:hidden WHERE uuid=:uuid",
                    {"name":account.name,"email":account.email,"password":account.password,"hidden":account.hidden,"uuid":uuid.UUID(account.uuid)})
    Conn.commit()
    
def RemoveAccount(accountUUID:str):
    cur = Conn.cursor()
    cur.execute("DELETE FROM accounts WHERE uuid=:uuid", {"uuid": uuid.UUID(accountUUID)})
    Conn.commit()

def LoadAccount(accountUUID:str):
    cur = Conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE uuid=:uuid", {"uuid": uuid.UUID(accountUUID)})
    result = cur.fetchone()
    return result

def LoadAllAccounts():
    cur = Conn.cursor()
    cur.execute("SELECT * FROM accounts")
    result = cur.fetchall()
    return result
    

def UuidInUse(accountUUID:str) -> bool:
    cur = Conn.cursor()
    cur.execute("SELECT name FROM accounts WHERE uuid=:uuid", {"uuid": uuid.UUID(accountUUID)})
    result = cur.fetchone()
    return result is not None

def EmailInUse(email:str) -> bool:
    result = Conn.cursor().execute("SELECT name FROM accounts WHERE email=:email", {"email": email}).fetchone()
    return (result is not None)


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