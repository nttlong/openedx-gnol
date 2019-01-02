import pymodel
import pydocs
import pyfuncs
import pyaggregatebuilders
import pyquery
class UserInfo(pymodel.BaseEmbededDoc):
    def __init__(self):
        self.email=str
class Users(pymodel.BaseModel):
    def __init__(self):
        self.name=UserInfo()



class Employees(pymodel.BaseModel):
   def __init__(self):
        import datetime
        self.set_model_name("employees")
        self.firstname=str
        self.lastname=str
        self.bithdate=datetime.datetime
employees=Employees()
qr=pyquery.query(employees.get_model_name())
qr.project(
    employees.firstname,
    employees.lastname

)
print qr.pipeline
# user=Users()
# c=pydoc.document.nam + pydoc.document.x>("1+{0}+3",15)
# print c
# pyaggregatebuilders.Match(pydoc.FilterFiels)
# c=pyaggregatebuilders.Project(
#     pydoc.document.fullName<<("concat(firstName,'{0}',lastName)","xxx")
#
# )
# print c
# c=(pyfuncs.regex(pydoc.document.name,"12"))
# print c