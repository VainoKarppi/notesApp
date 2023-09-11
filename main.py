

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



def Login():
    username = input("Enter username or email:\n")
    password = input("Enter password:\n")

    isEmail = '@' in username
    fetchedAccounts = []
    if isEmail:
        fetchedAccounts = [x for x in Accounts if x.email == username]
    else:
        fetchedAccounts = [x for x in Accounts if x.name == username]
    for account in fetchedAccounts:
        #TODO what if there is a username and same password is use for two accounts?? (Ask for email)
        hashedPassword = ComputeMD5hash(password,account.salt)
        if hashedPassword == account.password:
            print(f"Account: [({account.name}) | ({account.uuid})] Logged in!")   
            return account
        
    print(f"Invalid username or password! ({username})")
    return None

# Returns True if successfully removed. False if not
def RemoveAccount(uuid):
    import json
    print(f"Remoing account... ({uuid})")

    account = None
    isEmail = '@' in uuid
    if isEmail:
        account = next((x for x in Accounts if x.email == uuid), None)
    else:
        account = next((x for x in Accounts if x.uuid == uuid), None)

    if account is None:
        print("Cannot find user with this uuid!")
        return False
    
    Accounts.remove(account)
    jsonData = json.dumps([item.__dict__ for item in Accounts])

    # Overwrite ALL instead of add single
    with open('accounts.json', 'r+') as outfile:
        outfile.write(jsonData)
        outfile.close()
    return True


# Returns create Account class
def AddAccount(name, password, email):
    import json
    
    print(f"Creating account... ({name}) - ({email})\n")

    if '@' in name:
        print("Username cannot be email!")
        return None
    if '@' not in email:
        print("Invalid Email!")
        return None

    emailInUse = next((x for x in Accounts if x.email == email), None) != None
    if (emailInUse):
        print("Email already in use!")
        return None
    
    account = Account(name,password,email)
    Accounts.append(account)
    
    jsonData = json.dumps([item.__dict__ for item in Accounts])

    # Overwrite ALL instead of add single
    with open('accounts.json', 'r+') as outfile:
        outfile.write(jsonData)
        outfile.close()

    return account


def RemoveAccounts():
    import os
    if os.stat("accounts.json").st_size == 0: return

    
    open('accounts.json', 'w').close()
    global Accounts
    Accounts = []

def RestoreAccounts():
    print("Restoring accounts...")
    import json
    import os

    if os.stat("accounts.json").st_size == 0: return
    with open('accounts.json', 'r') as data:
        accounts = json.load(data)

    global Accounts
    for account in accounts:
        loadedAccount = Account(account['name'],account['password'],account['email'],account['uuid'],account['salt'])
        Accounts.append(loadedAccount)

    print(f"Restored {len(Accounts)} account(s)...\n")

def ComputeMD5hash(password,salt):
    import hashlib
    result = hashlib.md5((password + salt).encode())
    return (result.hexdigest())



def IsMD5hash(password: str) -> bool:
    import re
    return bool(re.match(r"^[a-fA-F0-9]{32}$", password))









#! --------------------
#! USER INTERFACE
#! --------------------
def CommandsHelp():
    print(f"\nHelp - (Show this help page)")
    print(f"Login - (Login to account)")
    print(f"Logout - (Login to account)")
    print(f"AddAccount - (Create Account)")
    print(f"RemoveAccount - (Remove Account)")
    print(f"ViewAccount - (Shows account info)")
    print(f"ShowAccounts - (Show All Accounts)")
    print(f"Exit - (Closes Program)\n")



if __name__=='__main__':
    print("STARTING PROGRAM...\n")
    RestoreAccounts()
    CommandsHelp()
    AddAccount("admin","admin","test@gmail.com")

    loggedUser = None
    while 1==1:
        command = input("\nEnter command:\n").lower()
        if (command == "help"): CommandsHelp()
        if (command == "login"): loggedUser = Login()
        if (command == "logout"):
            loggedUser = None
            print(f"User [{loggedUser.name}- ({loggedUser.uuid})] Logged Out!")

        if (command == "addaccount"): 
            username = input("Enter username:\n")
            password = input("Enter password:\n")
            email = input("Enter email:\n")
            AddAccount(username,password,email)
        if (command == "removeaccount"):
            uuid = input("Enter user email or uuid\n")
            RemoveAccount(uuid)

        if (command == "viewaccount"):
            if (loggedUser is None):
                print("Not logged in!")
            else:
                print(loggedUser)

        if (command == "showaccounts"):
            index = 0
            for account in Accounts:
                index = index + 1
                print(f"ACCOUNT: ({index})")
                print(account)

        if (command == "exit"): break

    #Reset accounts!
    #RemoveAccounts()

    print("\nEND\n")