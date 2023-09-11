Accounts = []
class Account:
    def __init__(self, name, password, uuid = None, salt = None):
        from uuid import uuid4
        from random import randint
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.name = name
        self.salt = str(randint(1000000,9999999)) if salt is None else salt
        self.password = password if IsMD5hash(password) else str(ComputeMD5hash(password,self.salt))
        

