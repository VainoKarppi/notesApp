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

Conn = sqlite3.connect("notes.db", detect_types=sqlite3.PARSE_DECLTYPES)
Cursor = Conn.cursor()


def ConnectionOpen():
    try:
        Conn.cursor()
        return True
    except Exception as ex:
        return False


def Init():
    try:
        
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
    Cursor.execute("INSERT INTO accounts (uuid,name,salt,email,password,admin,creationtimeutc,hidden) VALUES (?,?,?,?,?,?,?,?)",
                   (account.uuid, account.name, account.salt, account.email, account.password, account.admin, str(account.creationTimeUTC) ,account.hidden))
    Conn.commit()

def UpdateAccount(account) -> bool:
    try:
        Cursor.execute("UPDATE accounts SET name=:name, email=:email, password=:password, hidden=:hidden WHERE uuid=:uuid",
            {"name":account.name,"email":account.email,"password":account.password,"hidden":account.hidden,"uuid":account.uuid})
        Conn.commit()
        return True
    except:
        return False
    

def RemoveAccount(accountUUID:uuid.UUID):
    Cursor.execute("DELETE FROM accounts WHERE uuid=:uuid", {"uuid": accountUUID})
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
    Cursor.execute("INSERT INTO notes (owner,subject,text,creationTimeUTC,hidden) VALUES (?,?,?,?,?)",(note.ownerUUID, note.subject, note.text, note.creationTimeUTC, note.hidden))

def UpdateNote(note):
    Cursor.execute("UPDATE notes SET subject = ?, text = ?, hidden = ?, WHERE owner = ? AND subject = ?",(note.subject, note.text, note.hidden, note.ownerUUID, note.subject))

def RemoveNote(note): # DONT USE! (Use update with hidden=true)
    Cursor.execute("DELETE FROM notes WHERE owner = ? AND subject = ?",(note.ownerUUID, note.subject))

def LoadNote(owner: str, subject: str):
    Cursor.execute("SELECT * FROM notes WHERE owner = ? AND subject = ?",(owner, subject))