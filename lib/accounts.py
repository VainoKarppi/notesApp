import datetime
import lib.sqlitedb as db

#! ----------------------
#! ACCOUNTS FUNCTIONS
#! ----------------------
Accounts = []
class Account:
    def __init__(self, name:str, password:str, email:str, uuid:str = None, salt:int = None):
        from uuid import uuid4
        from random import randint
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.name = name
        self.salt = (randint(1000000,9999999)) if salt is None else salt
        self.email = email
        self.password = password if IsSHA3hash(password) else ComputeSHA3hash(password,self.salt)
        self.admin:bool = False
        self.hidden = False
    
    def __str__(self):
        return(f"\tuuid: {self.uuid}\n\tname: {self.name}\n\tpassword: {self.password}\n\temail: {self.email}\n\tsalt: {self.salt}\n")



def Login(usernameOrEmail: str, password: str) -> Account:
    result = db.Conn.cursor().execute("SELECT * FROM accounts WHERE name=:data COLLATE NOCASE OR email=:data COLLATE NOCASE", {"data": usernameOrEmail}).fetchone()
    if (result is None): raise ValueError(f"Invalid username or email! ({usernameOrEmail})")

    account = Account(result[1],result[4],result[3],result[0],result[2])
    account.admin = bool(result[5])

    #TODO what if there is a username and same password is use for two accounts?? (Ask for email) 😬
    hashedPassword = ComputeSHA3hash(password,account.salt)
    if hashedPassword == account.password:
        print(f"Account: [({account.name}) | ({account.uuid})] Logged in!")   
        return account
        
    raise ValueError(f"Invalid username or password! ({usernameOrEmail})")

# Returns True if successfully removed. False if not
def RemoveAccount(uuidOrEmail:str) -> None:
    print(f"Removing account... ({uuidOrEmail})")

    result = db.Conn.cursor().execute("DELETE FROM accounts WHERE uuid=:data OR email=:data COLLATE NOCASE", {"data": uuidOrEmail}).fetchone()
    print(result)



# Returns create Account class
def AddAccount(name:str, password:str, email:str, admin:bool = False) -> Account:
    print(f"Creating account... ({name}) - ({email})\n")

    if '@' in name: raise ValueError("Username cannot be email!")
    if '@' not in email: raise ValueError("Invalid Email!")

    result = db.Conn.cursor().execute("SELECT * FROM accounts WHERE name=:name COLLATE NOCASE OR email=:email COLLATE NOCASE", {"name":name, "email":email}).fetchone()
    if (result is not None): raise ValueError("Email or Username already in use!")
    
    account = Account(name,password,email)
    account.admin = admin
    
    db.InsertAccount(account)

    return account



def RemoveAccounts() -> None:
    print("Clearing all saved accounts...")
    db.Conn.cursor().execute("TRUNCATE TABLE accounts")

def IsUserSessionValid(uuid: str) -> bool:
    return db.UuidInUse(uuid)


def ComputeSHA3hash(password: str, salt: int) -> str:
    import hashlib
    result = hashlib.sha3_256()
    result.update((password + str(salt)).encode())
    return (result.hexdigest())


def IsSHA3hash(password:str) -> bool:
    import re
    return bool(re.match(r"^[a-fA-F0-9]{64}$", password))


