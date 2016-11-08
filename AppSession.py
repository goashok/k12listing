import web
from collections import defaultdict

class AppSession:
    def flash(self, group, message):
        if hasattr(web.ctx, 'session'):
            appSession = web.ctx.session
            appSession.flash[group].append(message)

    def clearFlash(self):
        if hasattr(web.ctx, 'session'):
            appSession = web.ctx.session
            appSession.flash = defaultdict(list)