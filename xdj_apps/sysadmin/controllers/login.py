import xdj


@xdj.controllers.Controller(
    url="login",
    template="login.html"
)
class LoginController(xdj.BaseController):
    def __init__(self):
        from django.conf import settings
        self.supportLanguages=[]
        for k,v in settings.LANGUAGE_DICT.items():
            if k in ["vi","en"]:
                self.supportLanguages.append(
                    xdj.dobject(
                        value = k,
                        caption =v
                        )
                )
    def on_get(selfs,sender):
        if isinstance(sender, xdj.Model):
            sender.username=""
            sender.isError=False
            sender.languages=selfs.supportLanguages
            return selfs.render(sender)
    def on_post(selfs,sender):
        if isinstance(sender, xdj.Model):
            sender.languages = selfs.supportLanguages
            from django.contrib.auth import authenticate, login
            user = authenticate(username=sender.post_data.username[0], password=sender.post_data.password[0])
            if user is not None:
                login(sender.request, user)
                return sender.redirect(sender.appUrl)
            else:
                sender.isError=True

            sender.username=sender.post_data.username[0]
        return selfs.render(sender)