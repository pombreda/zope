##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the gts ZCML namespace directives.

$Id: test_directives.py,v 1.11 2004/03/05 22:09:10 jim Exp $
"""
import os
import unittest
import threading
import time

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import implements

from zope.app import zapi
from zope.app.component.metaconfigure import managerHandler, provideInterface
from zope.app.mail.interfaces import \
     IMailDelivery, IMailer, ISMTPMailer, ISendmailMailer
from zope.app.mail.delivery import QueueProcessorThread
from zope.app.mail import delivery
from zope.app.tests import ztapi
import zope.app.mail.tests


class MaildirStub:

    def __init__(self, path, create=False):
        self.path = path
        self.create = create

    def __iter__(self):
        return iter(())

    def newMessage(self):
        return None

class Mailer:
    implements(IMailer)


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        self.testMailer = Mailer()

        ztapi.provideUtility(IMailer, Mailer(), name="test.smtp")
        ztapi.provideUtility(IMailer, self.testMailer, name="test.mailer")

        self.context = xmlconfig.file("mail.zcml", zope.app.mail.tests)
        self.orig_maildir = delivery.Maildir
        delivery.Maildir = MaildirStub
        
    def tearDown(self):
        delivery.Maildir = self.orig_maildir

        # Tear down the mail queue processor thread.
        # Give the other thread a chance to start:
        time.sleep(0.001)
        threads = list(threading.enumerate())
        for thread in threads:
            if isinstance(thread, QueueProcessorThread):
                thread.stop()
                thread.join()
                
    def testQueuedDelivery(self):
        delivery = zapi.getUtility(None, IMailDelivery, "Mail")
        self.assertEqual('QueuedMailDelivery', delivery.__class__.__name__)
        testdir = os.path.dirname(zope.app.mail.tests.__file__)
        self.assertEqual(os.path.join(testdir, 'mailbox'),
                         delivery.queuePath)

    def testDirectDelivery(self):
        delivery = zapi.getUtility(None, IMailDelivery, "Mail2")
        self.assertEqual('DirectMailDelivery', delivery.__class__.__name__)
        self.assert_(self.testMailer is delivery.mailer)

    def testSendmailMailer(self):
        mailer = zapi.getUtility(None, IMailer, "Sendmail")
        self.assert_(ISendmailMailer.providedBy(mailer))

    def testSMTPMailer(self):
        mailer = zapi.getUtility(None, IMailer, "smtp")
        self.assert_(ISMTPMailer.providedBy(mailer))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
