##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""mail ZCML Namespace handler

$Id$
"""
from zope.configuration.exceptions import ConfigurationError

from zope.security.checker import InterfaceChecker, CheckerPublic

from zope.app import zapi
from zope.app.component.metaconfigure import handler, proxify, PublicPermission
from zope.app.mail.delivery import QueuedMailDelivery, DirectMailDelivery
from zope.app.mail.delivery import QueueProcessorThread
from zope.app.mail.interfaces import IMailer, IMailDelivery
from zope.app.mail.mailer import SendmailMailer, SMTPMailer


def _assertPermission(permission, interfaces, component):
    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(interfaces, permission)

    return proxify(component, checker)
    

def queuedDelivery(_context, permission, queuePath, mailer, name="Mail"):

    def createQueuedDelivery():
        delivery = QueuedMailDelivery(queuePath)
        delivery = _assertPermission(permission, IMailDelivery, delivery)

        utilities = zapi.getGlobalService('Utilities')
        handler('Utilities', 'provideUtility', IMailDelivery, delivery, name)

        mailerObject = zapi.queryUtility(IMailer, mailer)
        if mailerObject is None:
            raise ConfigurationError("Mailer %r is not defined" %mailer)

        thread = QueueProcessorThread()
        thread.setMailer(mailerObject)
        thread.setQueuePath(queuePath)
        thread.setDaemon(True)
        thread.start()

    _context.action(
            discriminator = ('delivery', name),
            callable = createQueuedDelivery,
            args = () )


def directDelivery(_context, permission, mailer, name="Mail"):

    def createDirectDelivery():
        mailerObject = zapi.queryUtility(IMailer, mailer)
        if mailerObject is None:
            raise ConfigurationError("Mailer %r is not defined" %mailer)

        delivery = DirectMailDelivery(mailerObject)
        delivery = _assertPermission(permission, IMailDelivery, delivery)

        utilities = zapi.getGlobalService('Utilities')
        handler('Utilities', 'provideUtility', IMailDelivery, delivery, name)

    _context.action(
            discriminator = ('utility', IMailDelivery, name),
            callable = createDirectDelivery,
            args = () )


def sendmailMailer(_context, name,
                   command="/usr/lib/sendmail -oem -oi -f %(from)s %(to)s"):
    _context.action(
        discriminator = ('utility', IMailer, name),
        callable = handler,
        args = ('Utilities', 'provideUtility',
                IMailer, SendmailMailer(command), name)
        )

def smtpMailer(_context, name, hostname="localhost", port="25",
               username=None, password=None):
    _context.action(
        discriminator = ('utility', IMailer, name),
        callable = handler,
        args = ('Utilities', 'provideUtility',
                IMailer, SMTPMailer(hostname, port, username, password), name)
        )
