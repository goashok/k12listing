import config
import web
from collections import defaultdict


def flash(group, message):
    session.flash[group].append(message)


def flash_messages(group=None):
    if not hasattr(web.ctx, 'flash'):
        web.ctx.flash = session.flash
        session.flash = defaultdict(list)
    if group:
        return web.ctx.flash.get(group, [])
    else:
        return web.ctx.flash  

class Flash:
    def __init__(self, render):
        t_globals = web.template.Template.globals
        t_globals['datestr'] = web.datestr
        t_globals['app_version'] = lambda: VERSION + ' - ' + config.env
        t_globals['flash_messages'] = flash_messages
        t_globals['render'] = lambda t, *args: render._template(t)(*args)

      	

