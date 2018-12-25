#database utils
from pymongo import MongoClient

class MongoDB():
    #TODO:Verification parameter
    def __init__(self, mongo_host, mongo_port, db, coll='test', username=None, password=None):
        self.conn = MongoClient(host=mongo_host, port=mongo_port)
        self.db = db
        self.coll = coll
        if username and password:
            self.conn[self.db].authenticate(username, password)
        self.cursor = self.conn[self.db][self.coll]
    
    def select_coll(self, coll):
        self.cursor = self.conn[self.db][coll]
        return self.cursor
    
    def use_db(self, db,coll='test'):
        self.cursor = self.conn[db][coll]
        return self.cursor
        
    def insert_one(self, data):
        self.cursor.insert_one(data)


if __name__ == "__main__":
    HOST = 'xxx.xx.xx.xx'
    PORT = xxx
    DB = 'xxx'
    COLL = 'xxx'
    USERNAME = 'xxx'
    PASSWORD = 'xxxxxxxxx'
    mongo = MongoDB(HOST, PORT, DB, COLL, USERNAME, PASSWORD)




