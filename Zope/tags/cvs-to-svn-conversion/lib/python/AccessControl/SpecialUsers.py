##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Place to find special users

This is needed to avoid a circular import problem.  The 'real' values
are stored here by the AccessControl.User module as part of it's
initialization.

$Id: SpecialUsers.py,v 1.5 2003/07/11 14:21:30 fdrake Exp $
"""
__version__='$Revision: 1.5 $'[11:-2]

nobody = None
system = None
emergency_user = None

# Note: use of the 'super' name is deprecated.
super = None
