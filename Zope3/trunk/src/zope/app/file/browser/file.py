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
"""File views.

$Id: file.py,v 1.6 2004/03/19 03:17:39 srichter Exp $
"""
from zope.app.form.browser import BytesAreaWidget
from zope.app.form import CustomWidgetFactory

class FileView(object):

    def show(self):
        """Call the File"""
        request = self.request
        if request is not None:
            request.response.setHeader('Content-Type',
                                       self.context.contentType)
            request.response.setHeader('Content-Length',
                                       self.context.getSize())

        return self.context.data


class FileTextEdit(object):
    """File editing mix-in that uses a file-upload widget.
    """

    data_widget = CustomWidgetFactory(BytesAreaWidget)
