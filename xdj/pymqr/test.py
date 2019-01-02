import compilers
import pyquery
import pymongo
from pymongo import MongoClient
import pyfuncs
import pydocs
Fields=pydocs.Fields()
# print pyfuncs.toDouble(X.name)

# fields=pydoc.Fields()
# x=pyfuncs.cmp(fields.amount,fields.name)==0
# print isinstance(x,pydoc.Fields)
# # c=x.__owner__
# print x.__tree__
cnn=MongoClient(host="localhost",
                port=27017)
db=cnn.get_database("hrm")
db.authenticate(name="root",password="123456")
qr=pyquery.query(db,"test.coll001")
qr=qr.where(pyfuncs.regex(Fields.fx,"^312313$"))



# qr.project({
#     Fields.Users.username:1,
#     Fields.Users.fullName:pyfuncs.concat(Fields.Users.firstName, " ",Fields.Users.lastname)
# })

# qr=qr+2
#     #.set(x=1,y=2)
# import pprint
# items=list(qr.objects)
import pprint
x=list(qr.objects)
pprint.pprint(list(qr.items))

# ret=qr=pyquery.query(db,"test.coll001").insert(dict(
#     name=1
# ),dict(
#     fx="312313"
# )).commit()
# print ret
# qr=pyquery.query(db,"test").lookup(
#     From="ddd",
#     locaField="vvv",
#     foriegbField="ggg",
#     alias="ggg"
#
# ).lookup(
#     From="bbb",
#     pipeline="bbbb",
#     let="bbbb",
#     alias="bbbbb",
#
# )


# import expression_parser
# x=expression_parser.to_mongobd("x=={0}",'aaa')
# # expr,params=expression_parser.parse("$x==@test1",test1=2,username='admin')
# print qr.pipeline
#print params