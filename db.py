import pymongo, uuid

class DB:

    def __init__(self,name):
        self.db = pymongo.MongoClient('localhost', 27017)[name]

    def insert_into(self,collection,data):
        if '_id' not in data: data['_id'] = str(uuid.uuid4())
        self.db[collection].insert_one(data)

    def insert_many(self,collection,data):
        self.db[collection].insert_many(data)

    def get_from(self, collection, uid):
        return self.db[collection].find_one({"_id": uid})

    def remove_from(self, collection, predicate):
            return self.db[collection].remove(predicate)

    def find_in(self, collection, predicate=None):
        return self.db[collection].find(predicate) or []

    def update_with(self, collection, uid, data):
        record = self.get_from(collection, uid)
        record.update(data)
        self.db[collection].replace_one({'_id':uid}, record)

