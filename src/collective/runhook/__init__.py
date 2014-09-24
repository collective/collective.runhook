# -*- coding: utf-8 -*-
import csv
import os
import tempfile

from pkg_resources import iter_entry_points


def get_entrypoint(name):
    for ep in iter_entry_points('collective.runhook'):
        if ep.name == name:
            return ep
    raise KeyError(name)


def runhook(self, *args):
    """Execute named run hooks from installed packages

    usage: runhook [hooks]

    $ bin/instance runhook whoami

    $ bin/instance -OPlone runhook whoami

    $ ZOPE_USER=admin bin/instance -OPlone runhook whoami

    https://pypi.python.org/pypi/collective.runhook
    """

    # Parse hooks from arguments
    if len(self.options.args) == 1:
        hooks = csv.reader(self.options.args, delimiter=' ').next()[1:]
    else:
        hooks = self.options.args[1:]
    if not hooks:
        print "usage: runhook [hooks]"
        return

    # Build cmd to call all hooks
    if self.options.object_path:
        hook = '''\
# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from zope.globalrequest import getRequest

site = getSite()
context = obj
request = getRequest()

'''
    else:
        hook = '''\
# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from zope.globalrequest import getRequest

site = app
context = app
request = getRequest()

'''

    # Zope user
    if os.environ.get('ZOPE_USER'):
        hook += '''
from AccessControl.SecurityManagement import newSecurityManager

if site.acl_users.getUser('{0:s}'):
    newSecurityManager(
        request,
        site.acl_users.getUser('{0:s}')
    )
elif app.acl_users.getUser('{0:s}'):
    newSecurityManager(
        request,
        app.acl_users.getUser('{0:s}').__of__(site.acl_users)
    )
else:
    raise KeyError('{0:s}')
'''.format(os.environ.get('ZOPE_USER'))

    for ep in map(get_entrypoint, hooks):
        hook += '''\
import {0:s}
{0:s}.{1:s}(context, request)
'''.format(ep.module_name, ep.name)

    # Execute
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(hook)
        temp.flush()
        cmdline = self.get_startup_cmd(self.options.python,
                                       'execfile(r\'%s\')' % temp.name)
        self._exitstatus = os.system(cmdline)


def whoami(context, request):
    from AccessControl.SecurityManagement import getSecurityManager
    user = getSecurityManager().getUser()

    from pprint import pprint
    pprint({
        'context': context.__repr__(),
        'user': user.__repr__(),
        'getId': user.getId(),
        'getUserName': user.getUserName(),
#       'getDomains': user.getDomains(),
        'getRoles': user.getRoles(),
        'getRolesInContext': user.getRolesInContext(context)
    })
