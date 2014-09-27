Implement your script in some module shipping in your package as a named
function accepting context and request as its arguments:

..  code:: python

    def whoami(context, request):
        from AccessControl.SecurityManagement import getSecurityManager
        user = getSecurityManager().getUser()
        return {
            'absolute_url': context.absolute_url(),
            'context': context.__repr__(),
            'user': user.__repr__(),
            'getId': user.getId(),
            'getUserName': user.getUserName(),
            'getRoles': user.getRoles(),
            'getRolesInContext': user.getRolesInContext(context)
        }

Remember to include transaction commit when your scripts modifies the
database (the example above does not):

..  code:: python

    import transaction
    transaction.commit()

Register your function as a named set'uptools entry point for
*collective.runhook** in your package's **setup.py**:

..  code:: python

    from setuptools import setup

    setup(
        # ...
        entry_points="""
        # -*- Entry points: -*-
        # ...
        [collective.runhook]
        whoami = my.package:whoami
        """
    )

Add **collective.runhook** as a dependency of your package, or include it in
your buildout's instance part:

..  code:: ini

    [buildout]
    parts = instance
    # ...

    [instance]
    recipe = plone.recipe.zope2instance
    # ...
    eggs =
        Plone
    #   ...
        collective.runhook

Run the buildout and execute your script:

..  code:: bash

    $ bin/instance runhook whoami
    ...
    {'absolute_url': 'http://nohost/Plone',
     'context': '<Application at >',
     'getId': None,
     'getRoles': ('manage', 'Authenticated'),
     'getRolesInContext': ['manage', 'Authenticated'],
     'getUserName': 'System Processes',
     'user': "<UnrestrictedUser 'System Processes'>"}

**collective.runhook** obeys the same instance script arguments as
the run command:

..  code:: bash

    $ bin/instance -OPlone runhook whoami
    ...
    {'absolute_url': 'http://nohost/Plone',
     'context': '<PloneSite at /Plone>',
     'getId': None,
     'getRoles': ('manage', 'Authenticated'),
     'getRolesInContext': ['manage', 'Authenticated'],
     'getUserName': 'System Processes',
     'user': "<UnrestrictedUser 'System Processes'>"}

As a bonus, **collective.runhook** can authenticate the script as any existing
user given with ``ZOPE_USER`` environment variable (but be aware that the
authentication is only done after ``-O``-traverse):

..  code:: bash

    $ ZOPE_USER=datakurre bin/instance -OPlone runhook whoami
    ...
    {'absolute_url': 'http://nohost/Plone',
     'context': '<PloneSite at /Plone>',
     'getId': 'datakurre',
     'getRoles': ['Member', 'Reviewer', 'Site Administrator', 'Authenticated'],
     'getRolesInContext': ['Member',
                           'Reviewer',
                           'Site Administrator',
                           'Authenticated'],
     'getUserName': 'datakurre',
     'user': "<PloneUser 'datakurre'>"}

And we do support URLs with VirtualHostBase:

    $ ZOPE_USER=datakurre bin/instance -O/VirtualHostBase/http://example.com:80/Plone/VirtualHostRoot/Plone runhook whoami
    ...
    {'absolute_url': 'http://example.com',
     'context': '<PloneSite at /Plone>',
     'getId': 'datakurre',
     'getRoles': ['Member', 'Reviewer', 'Site Administrator', 'Authenticated'],
     'getRolesInContext': ['Member',
                           'Reviewer',
                           'Site Administrator',
                           'Authenticated'],
     'getUserName': 'datakurre',
     'user': "<PloneUser 'datakurre'>"}
