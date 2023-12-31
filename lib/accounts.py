from datetime import datetime
import uuid
import lib.sqlitedb as db

#! ----------------------
#! ACCOUNTS FUNCTIONS
#! ----------------------

class Account:
    def __init__(self, name:str, password:str, email:str, uuid:uuid.UUID = None, salt:int = None):
        from uuid import uuid4
        from random import randint
        self.uuid = (uuid4()) if uuid is None else uuid
        self.name = name
        self.salt = (randint(1000000,9999999)) if salt is None else salt
        self.email = email
        self.password = password if IsSHA3hash(password) else ComputeSHA3hash(password,self.salt)
        self.admin:bool = False
        self.creationTimeUTC = datetime.utcnow()
        self.hidden = False
    
    def __str__(self):
        return(f"\tuuid: {self.uuid}\n\tname: {self.name}\n\tpassword: {self.password}\n\temail: {self.email}\n\tsalt: {self.salt}\n\tadmin: {self.admin}")



def Login(usernameOrEmail: str, password: str) -> Account:
    result = db.Cursor.execute("SELECT * FROM accounts WHERE name=:data COLLATE NOCASE OR email=:data COLLATE NOCASE", {"data": usernameOrEmail}).fetchone()
    if (result is None): raise ValueError("Invalid credientials!")

    account = Account(result[1],result[4],result[3],result[0],result[2])
    account.admin = bool(result[5])
    account.creationTimeUTC = datetime.strptime(result[6],'%Y-%m-%d %H:%M:%S.%f')
    account.hidden = bool(result[7])

    #TODO what if there is a username and same password is use for two accounts?? (Ask for email) 😬
    hashedPassword = ComputeSHA3hash(password,account.salt)
    if hashedPassword == account.password:
        if (account.hidden): raise Exception("Account disabled!")
        return account
        
    raise ValueError("Invalid credientials!")


def RemoveAccount(uuidOrEmail:str) -> None:
    userUuid = None
    if ('@' not in uuidOrEmail):
        if (isinstance(uuidOrEmail, uuid.UUID)):
            userUuid = uuidOrEmail
        else:
            userUuid = uuid.UUID(uuidOrEmail)

    if (userUuid is not None and db.UuidInUse(userUuid) == False): raise ValueError("UUID not found!")
    
    result = db.Cursor.execute("DELETE FROM accounts WHERE uuid=:uuid OR email=:email COLLATE NOCASE", {"uuid":userUuid, "email":uuidOrEmail})
    if (result.rowcount == 0): raise Exception("Unable to remove account!")
    db.Conn.commit()


def GetAccount(uuidOrEmail: uuid.UUID | str) -> Account:

    userUuid:uuid.UUID = None
    if (isinstance(uuidOrEmail, uuid.UUID)): userUuid = uuidOrEmail
    
    result = db.Cursor.execute("SELECT * FROM accounts WHERE uuid=:uuid COLLATE NOCASE OR email=:email COLLATE NOCASE", {"uuid":userUuid, "email":uuidOrEmail}).fetchone()
    if (result is None): return None
    
    account = Account(result[1],result[4],result[3],result[0],result[2])
    account.admin = bool(result[5])
    account.creationTimeUTC = datetime.strptime(result[6],'%Y-%m-%d %H:%M:%S.%f')

    return account



# Returns create Account class
def CreateAccount(name:str, password:str, email:str, admin:bool = False) -> Account:
    if '@' in name: raise ValueError("Username cannot be email!")
    if '@' not in email: raise ValueError("Invalid Email!")

    result = db.Cursor.execute("SELECT * FROM accounts WHERE name=:name COLLATE NOCASE OR email=:email COLLATE NOCASE", {"name":name, "email":email}).fetchone()
    if (result is not None): raise ValueError("Email or Username already in use!")
    
    account = Account(name,password,email)
    account.admin = admin

    if(account is not None): db.InsertAccount(account)

    return account

def GetAllAccounts() -> list:
    accounts = []
    results = db.Cursor.execute("SELECT * FROM accounts WHERE hidden=:hidden", {"hidden":0}).fetchall()

    for result in results:
        account = Account(result[1],result[4],result[3],result[0],result[2])
        account.admin = bool(result[5])
        accounts.append(account)

    return accounts

def UpdateAccount(account: Account) -> None:
    result = db.UpdateAccount(account)
    if (result.rowcount == 0): raise Exception("Failed to update account!")


def UpdatePassword(account: Account, newPassword: str) -> None:
    oldPasswordHash = account.password

    newPasswordHash = ComputeSHA3hash(newPassword,account.salt)
    if (newPasswordHash == oldPasswordHash): raise ValueError("New Password cannot be same as old password!")
    if (len(newPassword) < 5): raise ValueError("New Password must be at least 5 characters")

    try:
        account.password = newPasswordHash
        UpdateAccount(account)
    except:
        account.password = oldPasswordHash # Restore old password if update was failed
        pass


def RemoveAllAccounts() -> None:
    db.Cursor.execute("TRUNCATE TABLE accounts")

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


