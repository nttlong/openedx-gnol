import xdj


def on_authenticate(sender):
    from django.contrib.auth.models import User
    try:
        User.objects.get(username="root")
    # except DoesNotExist, e:
    #     return None
    except User.DoesNotExist as ex:
        user = User.objects.create_user(username='root',
                                        email='root@root.com',
                                        password='root')
        user.is_active=True
        user.is_superuser=True
        user.save()


    if isinstance(sender, xdj.Model):
        if sender.user.is_anonymous():
            return False
    if not sender.user.is_active:
        return False
    if sender.user.is_superuser:
        return True
    return False
host_dir="sys"
app_name="sys-admin"
rel_login_url="login"
def on_get_language_resource_item(language,appname,view,key,value):
    return value