collective.runhook
==================

Named instance script run hooks for `plone.recipe.zope2instance`_.

.. _plone.recipe.zope2instance: https://pypi.python.org/pypi/plone.recipe.zope2instance

Implement your run hook in your package as a named Python function accepting
context and request as its arguments:

..  code:: python

    def whoami(context, request):
        from AccessControl.SecurityManagement import getSecurityManager
        user = getSecurityManager().getUser()

        from pprint import pprint
        pprint({
            'context': context.__repr__(),
            'user': user.__repr__(),
            'getId': user.getId(),
            'getUserName': user.getUserName(),
            'getRoles': user.getRoles(),
            'getRolesInContext': user.getRolesInContext(context)
        })

Remember to include transaction commit when you want to modify the database:

..  code:: python

    import transaction
    transaction commit

Register your function as a named hook for **collective.runhook** in your
packages **setup.py** as a setuptools entrypoint:

..  code:: python

    from setuptools import setup

    setup(
        ...
        entry_points="""
        # -*- Entry points: -*-
        ...
        [collective.runhook]
        whoami = my.package:whoami
        """
    )

Add **collective.runhook** as a dependency of your package, or include it in
your buildout's instance part:

..  code:: ini

    [buildout]
    parts = instance
    ...

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    eggs =
        Plone
        ...
        collective.runhook

Run the buildout and execute your hook as you wish:

..  code:: bash

    $ bin/instance runhook whoami
    ...
    {'context': '<Application at >',
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
    {'context': '<PloneSite at /Plone>',
     'getId': None,
     'getRoles': ('manage', 'Authenticated'),
     'getRolesInContext': ['manage', 'Authenticated'],
     'getUserName': 'System Processes',
     'user': "<UnrestrictedUser 'System Processes'>"}

As a bonus, **collective.runhook** can authenticate the hook as a user
given as ``ZOPE_USER`` environment variable:

..  code:: bash

    $ ZOPE_USER=datakurre bin/instance -OPlone runhook whoami
    ...
    {'context': '<PloneSite at /Plone>',
     'getId': 'datakurre',
     'getRoles': ['Member', 'Reviewer', 'Site Administrator', 'Authenticated'],
     'getRolesInContext': ['Member',
                           'Reviewer',
                           'Site Administrator',
                           'Authenticated'],
     'getUserName': 'datakurre',
     'user': "<PloneUser 'datakurre'>"}
