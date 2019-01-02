import xdj


@xdj.controllers.Controller(
    url="system/email_settings",
    template="system/email_settings.html"
)
class SystemEmailController(xdj.BaseController):
    def on_get(selfs,sender):
        if isinstance(sender, xdj.Model):
            return selfs.render(sender)
    def on_post(selfs,sender):
        if isinstance(sender, xdj.Model):
            pass
        return selfs.render(sender)