__db__ = None
def db():
    if __db__ == None:
        global __db__
        import pymongo
        config=db_config()
        cnn=pymongo.MongoClient(host=config["host"],port=config["port"])
        database = cnn.get_database(config["db"])
        database.authenticate(config["user"], config["password"])
        __db__ = database
    return __db__



def db_config():
    from django.conf import settings
    return dict(
        db=settings.CONTENTSTORE["DOC_STORE_CONFIG"]["db"],
        host=settings.CONTENTSTORE["DOC_STORE_CONFIG"]["host"],
        user=settings.CONTENTSTORE["DOC_STORE_CONFIG"]["user"],
        password=settings.CONTENTSTORE["DOC_STORE_CONFIG"]["password"],
        port=settings.CONTENTSTORE["DOC_STORE_CONFIG"]["port"]

    )
