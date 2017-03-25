import json

def decode(data): 
    try: return json.loads(data)
    except: return data
class Dot:
    def __init__(self,data={}): self.__dict__ = {k:(str(v) if k=="_id" else decode(v)) for k,v in data.items()}
    def __getitem__(self,key): return self.__dict__[key]
    def has(self,attr): return attr in self.__dict__
    def update(self,data): self.__dict__.update(data)
    def export(self,*fields): return dot({k:getattr(self,k) for k in fields})
    def nexport(self,*fields): return dot({k:getattr(self,k) for k in self.__dict__ if k not in fields})
    def dump(self): return self.__dict__
