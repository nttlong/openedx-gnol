import xdj
@xdj.Controller(
    url="login",
    template="login.html"
)
class LoginController(xdj.BaseController):
    def on_get(self,model):
        return self.render(model)
    def on_post(selfs,sender):
        if isinstance(sender, xdj.Model):
            from django.contrib.auth import authenticate, login
            user = authenticate(username=sender.post_data.username[0], password=sender.post_data.password[0])
            if user is not None:
                login(sender.request, user)
                if sender.request.GET.get("next",None) == None:
                    return sender.redirect(sender.appUrl)
                else:
                    return sender.redirect(sender.request.GET.get("next",None))
            else:
                sender.isError=True

            sender.username = sender.post_data.username[0]
        return selfs.render(sender)