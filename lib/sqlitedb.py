import datetime
import sqlite3
import uuid

import lib.accounts as accounts
import lib.notes as notes


def adapt_datetime(dt):
    return int(dt.strftime('%s'))

def convert_datetime(ts):
    return datetime.datetime.fromtimestamp(ts)

# SUPPORT FOR UUID/GUID FOR DATABASE
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

# SUPPORT FOR DATETIME FOR DATABASE
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('datetime', convert_datetime)



def ConnectionOpen():
    try:
        Conn.cursor()
        return True
    except:
        return False


def Init():
    try:
        # sqlite3.PARSE_DECLTYPES breaks the ability to use DATE. however it adds the ability to read UUID's!
        global Conn,Cursor
        Conn = sqlite3.connect("notesapp.db", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        Cursor = Conn.cursor()
        
        # Create accounts table
        Cursor.execute("""CREATE TABLE IF NOT EXISTS accounts (     
                    uuid GUID PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    salt INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    admin INTEGER NOT NULL,
                    creationtimeutc INTEGER NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        
        # Create Notes Table
        Cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
                    owner GUID NOT NULL,
                    subject TEXT NOT NULL,
                    text TEXT NOT NULL,
                    webpage TEXT NOT NULL,
                    creationTimeUTC INTEGER NOT NULL,
                    hidden INTEGER NOT NULL
                )""")
        

    except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)



# ACCOUNTS
def InsertAccount(account):
    result = Cursor.execute("INSERT INTO accounts (uuid,name,salt,email,password,admin,creationtimeutc,hidden) VALUES (?,?,?,?,?,?,?,?)",
                   (account.uuid, account.name, account.salt, account.email, account.password, account.admin, str(account.creationTimeUTC) ,account.hidden))
    if (result.rowcount == 0): raise Exception("Failed to insert account!")
    Conn.commit()

def UpdateAccount(account) -> sqlite3.Cursor:
    result = Cursor.execute("UPDATE accounts SET name=:name, email=:email, password=:password, hidden=:hidden WHERE uuid=:uuid",
        {"name":account.name,"email":account.email,"password":account.password,"hidden":account.hidden,"uuid":account.uuid})
    if (result.rowcount != 0): Conn.commit()
    return result
    

def RemoveAccount(accountUUID:uuid.UUID):
    result = Cursor.execute("DELETE FROM accounts WHERE uuid=:uuid", {"uuid": accountUUID})
    if (result.rowcount == 0): raise Exception("No account found to be removed!")
    Conn.commit()


def LoadAccount(accountUUID:uuid.UUID):
    Cursor.execute("SELECT * FROM accounts WHERE uuid=:uuid", {"uuid": accountUUID})
    result = Cursor.fetchone()
    return result


def LoadAllAccounts():
    Cursor.execute("SELECT * FROM accounts")
    result = Cursor.fetchall()
    return result
    

def UuidInUse(accountUUID:uuid.UUID) -> bool:
    result = Cursor.execute("SELECT hidden FROM accounts WHERE uuid=:uuid", {"uuid": accountUUID}).fetchone()
    return result is not None


def EmailInUse(email:str) -> bool:
    result = Cursor.execute("SELECT name FROM accounts WHERE email=:email", {"email": email}).fetchone()
    return (result is not None)


# NOTES
def InsertNote(note):
    result = Cursor.execute("INSERT INTO notes (owner,subject,text,webpage,creationTimeUTC,hidden) VALUES (?,?,?,?,?,?)",
                   (note.ownerUUID, note.subject, note.text, note.webPage, str(note.creationTimeUTC), note.hidden))
    if (result.rowcount == 0): raise Exception("Failed to insert note!")
    Conn.commit()

def UpdateNote(note) -> sqlite3.Cursor:
    result = Cursor.execute("UPDATE notes SET text=:text, hidden=:hidden WHERE owner=:owner AND subject=:subject COLLATE NOCASE",
        {"text":note.text,"hidden":note.hidden,"owner":note.ownerUUID,"subject":note.subject})
    if (result.rowcount != 0): Conn.commit()
    return result

def RemoveNote(ownerUUID:uuid.UUID, subject: str) -> sqlite3.Cursor: # SHOULD NOT BE USED! (Use update with hidden=true)
    result = Cursor.execute("DELETE FROM notes WHERE owner = ? AND subject = ? COLLATE NOCASE",[ownerUUID, subject])
    if (result.rowcount != 0): Conn.commit()
    return result

def GetNote(ownerUUID:uuid.UUID, subject: str):
    result = Cursor.execute("SELECT * FROM notes WHERE owner = ? AND subject = ? COLLATE NOCASE",[ownerUUID, subject]).fetchone()
    return result

def LoadAllUserNotes(ownerUUID:uuid.UUID):
    result = Cursor.execute("SELECT * FROM notes WHERE owner=:owner", {"owner": ownerUUID}).fetchall()
    return result

def LoadAllNotes():
    result = Cursor.execute("SELECT * FROM notes")
    return result

def RemoveAllUserNotes(ownerUUID: uuid.UUID) -> sqlite3.Cursor:
    result = Cursor.execute("DELETE FROM notes WHERE owner = ?",[ownerUUID])
    if (result.rowcount != 0): Conn.commit()
    return result

def FindNote(ownerUUID: uuid.UUID, what: str, type:str) -> list:
    #TODO Serialize type to safe
    data = Cursor.execute("SELECT * FROM notes WHERE owner = ? AND " + type + " LIKE ?",[ownerUUID,('%' + what + '%')]).fetchall()
    return data