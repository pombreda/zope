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
"""

$Id: DTMLPageEdit.py,v 1.3 2002/09/04 13:44:25 faassen Exp $
"""
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.Forms.Views.Browser import Widget
from Zope.App.Forms.Widget import CustomWidget
from Zope.App.Forms.Views.Browser.FormView import FormView
from Zope.App.OFS.Content.DTMLPage.DTMLPage import IDTMLPage

class DTMLPageEdit(FormView):
    form = ViewPageTemplateFile('edit.pt')
    schema = IDTMLPage
    custom_widgets = {'source': CustomWidget(Widget.TextAreaWidget,
                                             cols=80, rows=15)}
    fields_order = ('source',)
