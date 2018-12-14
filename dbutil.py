#database utils
from pymongo import MongoClient

class MongoDB():
    #TODO:Verification parameter
    def __init__(self, mongo_host, mongo_port, db, coll, username=None, password=None):
        self.conn = MongoClient(host=mongo_host, port=mongo_port)
        self.db = db
        self.coll = coll
        if username and password:
            self.conn[self.db].authenticate(username, password)
        self.cursor = self.conn[self.db][self.coll]
        
    def insert_one(self, data):
        self.cursor.insert_one(data)

if __name__ == "__main__":
    HOST = '118.24.141.137'
    PORT = 13014
    DB = 'data'
    COLL = 'test'
    USERNAME = 'hsx'
    PASSWORD = 'G5u9zenNcRof1JaU'
    mongo = MongoDB(HOST, PORT, DB, COLL, USERNAME, PASSWORD)





