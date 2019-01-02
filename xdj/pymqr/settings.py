__db__ = None
def setdb(db):
    global __db__
    __db__ = db
def getdb():
    return __db__
