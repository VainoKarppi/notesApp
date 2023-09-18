import datetime

#! ----------------------
#! ACCOUNTS FUNCTIONS
#! ----------------------
Accounts = []
class Account:
    def __init__(self, name, password, email, uuid = None, salt = None):
        from uuid import uuid4
        from random import randint
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.name = name
        self.salt = str(randint(1000000,9999999)) if salt is None else salt
        self.email = email
        self.password = password if IsMD5hash(password) else ComputeMD5hash(password,self.salt)
    
    def __str__(self):
        return(f"\tuuid: {self.uuid}\n\tname: {self.name}\n\tpassword: {self.password}\n\temail: {self.email}\n\tsalt: {self.salt}\n")



def Login(usernameOrEmail: str, password: str) -> Account:
    isEmail = '@' in usernameOrEmail
    fetchedAccounts = []
    if isEmail:
        fetchedAccounts = [x for x in Accounts if x.email.lower() == usernameOrEmail.lower()]
    else:
        fetchedAccounts = [x for x in Accounts if x.name == usernameOrEmail]
    for account in fetchedAccounts:
        #TODO what if there is a username and same password is use for two accounts?? (Ask for email) 😬
        hashedPassword = ComputeMD5hash(password,account.salt)
        if hashedPassword == account.password:
            print(f"Account: [({account.name}) | ({account.uuid})] Logged in!")   
            return account
        
    raise ValueError(f"Invalid username or password! ({usernameOrEmail})")

# Returns True if successfully removed. False if not
def RemoveAccount(uuidOrEmail) -> None:
    print(f"Removing account... ({uuidOrEmail})")

    account = None
    isEmail = '@' in uuidOrEmail
    if isEmail:
        account = next((x for x in Accounts if x.email.lower() == uuidOrEmail.lower()), None)
    else:
        account = next((x for x in Accounts if x.uuid == uuidOrEmail), None)

    Accounts.remove(account)
    UpdateAccounts()


# Returns create Account class
def AddAccount(name, password, email) -> Account:
    print(f"Creating account... ({name}) - ({email})\n")

    if '@' in name: raise ValueError("Username cannot be email!")
    if '@' not in email: raise ValueError("Invalid Email!")

    emailInUse = next((x for x in Accounts if x.email.lower() == email.lower()), None) != None
    if (emailInUse): raise ValueError("Email already in use!")
    
    account = Account(name,password,email)
    Accounts.append(account)
    
    UpdateAccounts(True)

    return account

def UpdateAccounts(append: bool = False) -> None:
    import json
    jsonData = json.dumps([item.__dict__ for item in Accounts])

    mode = 'r+' if append else 'w'
    with open('accounts.json', mode) as outfile: outfile.write(jsonData)

def RemoveAccounts() -> None:
    print("Clearing all saved accounts...")

    import os
    if os.stat("accounts.json").st_size == 0: return

    open('accounts.json', 'w').close()
    global Accounts
    Accounts = []


def RestoreAccounts() -> None:
    print("Restoring accounts...")

    import json
    import os

    if os.stat("accounts.json").st_size == 0: return
    with open('accounts.json', 'r') as data: accounts = json.load(data)

    global Accounts
    for account in accounts:
        loadedAccount = Account(account['name'],account['password'],account['email'],account['uuid'],account['salt'])
        Accounts.append(loadedAccount)

    print(f"Restored {len(Accounts)} account(s)...\n")


def IsUserSessionValid(uuid: str) -> bool:
    found = next((x for x in Accounts if x.uuid == uuid), None) != None
    return found


def ComputeMD5hash(password: str, salt: str) -> str:
    import hashlib
    result = hashlib.md5((password + salt).encode())
    return (result.hexdigest())


def IsMD5hash(password: str) -> bool:
    import re
    return bool(re.match(r"^[a-fA-F0-9]{32}$", password))


