import xdj


def on_authenticate(sender):
    return True
host_dir="lms"
app_name="gnol-lms"
rel_login_url="login"
def on_get_language_resource_item(language,appname,view,key,value):
    return value