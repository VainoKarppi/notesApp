Accounts = []
class Account:
    def __init__(self, name, password, uuid = None, salt = None):
        from uuid import uuid4
        from random import randint
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.name = name
        self.salt = str(randint(1000000,9999999)) if salt is None else salt
        self.password = password if IsMD5hash(password) else str(ComputeMD5hash(password,self.salt))
        


def RestoreAccounts():
    print("Restoring accounts...")
    import json
    import os

    if os.stat("accounts.json").st_size == 0: return
    with open('accounts.json', 'r') as data:
        accounts = json.load(data)

    global Accounts
    for account in accounts:
        loadedAccount = Account(account['name'],account['password'],account['uuid'],account['salt'])
        Accounts.append(loadedAccount)

    print(f"Restored {len(Accounts)} account(s)...\n")

def ComputeMD5hash(password,salt):
    import hashlib
    from hashlib import md5
    m = hashlib.md5()
    saltedPassword = password + salt
    m.update(saltedPassword.encode('utf-8'))
    md5string = m.digest()
    return md5string



def IsMD5hash(string: str) -> bool:
    import re
    return bool(re.match(r"^[a-fA-F0-9]{32}$", string))
