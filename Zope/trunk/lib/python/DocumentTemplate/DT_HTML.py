##############################################################################
#
# Copyright (c) 1996-1998, Digital Creations, Fredericksburg, VA, USA.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#   o Redistributions of source code must retain the above copyright
#     notice, this list of conditions, and the disclaimer that follows.
# 
#   o Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions, and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
# 
#   o All advertising materials mentioning features or use of this
#     software must display the following acknowledgement:
# 
#       This product includes software developed by Digital Creations
#       and its contributors.
# 
#   o Neither the name of Digital Creations nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
# 
# 
# THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS AND CONTRIBUTORS *AS IS*
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL
# CREATIONS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# 
# If you have questions regarding this software, contact:
#
#   Digital Creations, L.C.
#   910 Princess Ann Street
#   Fredericksburge, Virginia  22401
#
#   info@digicool.com
#
#   (540) 371-6909
#
##############################################################################

"""HTML formated DocumentTemplates

$Id: DT_HTML.py,v 1.13 1998/09/14 22:03:31 jim Exp $"""

from DT_String import String, FileMixin
import DT_String, regex
from DT_Util import ParseError, str
from string import strip, find, split, join, rfind

class dtml_re_class:

    def search(self, text, start=0,
               name_match=regex.compile('[\0- ]*[a-zA-Z]+[\0- ]*').match,
               end_match=regex.compile('[\0- ]*\(/\|end\)',
                                       regex.casefold).match,
               ):
        s=find(text,'<!--#',start)
        if s < 0: return s
        e=find(text,'-->',s)
        if e < 0: return e

        n=s+5
        l=end_match(text,n)
        if l > 0:
            end=strip(text[n:n+l])
            n=n+l
        else: end=''

        l=name_match(text,n)
        if l < 0: return l
        a=n+l
        name=strip(text[n:a])

        args=strip(text[a:e])

        d=self.__dict__
        d[0]=text[s:e+3]
        d[1]=end
        d['end']= end
        d[2]=name
        d['name']=name
        d[3]=args
        d['args']=args

        return s

    def group(self,*args):
        g=self.__dict__
        if len(args)==1: return g[args[0]]
        r=[]
        for arg in args:
            r.append(g[arg])
        return tuple(r)
        

class HTML(DT_String.String):
    """HTML Document Templates

    HTML Document templates use HTML server-side-include syntax,
    rather than Python format-string syntax.  Here's a simple example:

      <!--#in results-->
        <!--#var name-->
      <!--#/in-->

    HTML document templates quote HTML tags in source when the
    template is converted to a string.  This is handy when templates
    are inserted into HTML editing forms.
    """

    def tagre(self):
        return dtml_re_class()

    def parseTag(self, tagre, command=None, sargs=''):
        """Parse a tag using an already matched re

        Return: tag, args, command, coname

        where: tag is the tag,
               args is the tag\'s argument string,
               command is a corresponding command info structure if the
                  tag is a start tag, or None otherwise, and
               coname is the name of a continue tag (e.g. else)
                 or None otherwise
        """
        tag, end, name, args, =tagre.group(0, 'end', 'name', 'args')
        args=strip(args)
        if end:
            if not command or name != command.name:
                raise ParseError, ('unexpected end tag', tag)
            return tag, args, None, None

        if command and name in command.blockContinuations:

            if name=='else' and args:
                # Waaaaaah! Have to special case else because of
                # old else start tag usage. Waaaaaaah!
                l=len(args)
                if not (args==sargs or
                        args==sargs[:l] and sargs[l:l+1] in ' \t\n'):
                    return tag, args, self.commands[name], None
            
            return tag, args, None, name

        try: return tag, args, self.commands[name], None
        except KeyError:
            raise ParseError, ('Unexpected tag', tag)

    def SubTemplate(self, name): return HTML('', __name__=name)

    def varExtra(self,tagre): return 's'

    def manage_edit(self,data,REQUEST=None):
        'edit a template'
        self.munge(data)
        if REQUEST: return self.editConfirmation(self,REQUEST)

    def quotedHTML(self,
                   text=None,
                   character_entities=(
                       (('&'), '&amp;'),
                       (("<"), '&lt;' ),
                       ((">"), '&gt;' ),
                       (('"'), '&quot;'))): #"
        if text is None: text=self.read_raw()
        for re,name in character_entities:
            if find(text, re) >= 0: text=join(split(text,re),name)
        return text

    errQuote=quotedHTML

    def __str__(self):
        return self.quotedHTML()

    def management_interface(self):
        '''Hook to allow public execution of management interface with
        everything else private.'''
        return self

    def manage_editForm(self, PARENT_URL, REQUEST):
        '''Display doc template editing form''' #"
        
        return self._manage_editForm(
            self,
            mapping=REQUEST,
            __str__=str(self),
            PARENT_URL=PARENT_URL
            )

    manage_editDocument=manage=manage_editForm

class HTMLDefault(HTML):
    '''\
    HTML document templates that edit themselves through copy.

    This is to make a distinction from HTML objects that should edit
    themselves in place.
    '''
    copy_class=HTML

    def manage_edit(self,data,PARENTS,URL1,REQUEST):
        'edit a template'
        newHTML=self.copy_class(data,self.globals,self.__name__)
        setattr(PARENTS[1],URL1[rfind(URL1,'/')+1:],newHTML)
        return self.editConfirmation(self,REQUEST)


class HTMLFile(FileMixin, HTML):
    """\
    HTML Document templates read from files.

    If the object is pickled, the file name, rather
    than the file contents is pickled.  When the object is
    unpickled, then the file will be re-read to obtain the string.
    Note that the file will not be read until the document
    template is used the first time.
    """

    def manage_default(self, REQUEST=None):
        'Revert to factory defaults'
        if self.edited_source:
            self.edited_source=''
            self.cooked=self.cook()
        if REQUEST: return self.editConfirmation(self,REQUEST)

    def manage_editForm(self, PARENT_URL, REQUEST):
        '''Display doc template editing form'''

        return self._manage_editForm(mapping=REQUEST,
                                     document_template_edit_width=
                                     self.document_template_edit_width,
                                     document_template_edit_header=
                                     self.document_template_edit_header,
                                     document_template_form_header=
                                     self.document_template_form_header,
                                     document_template_edit_footer=
                                     self.document_template_edit_footer,
                                     PARENT_URL=PARENT_URL,
                                     __str__=str(self),
                                     FactoryDefaultString=FactoryDefaultString,
                                     )
    manage_editDocument=manage=manage_editForm

    def manage_edit(self,data,
                    PARENTS=[],URL1='',URL2='',REQUEST='', SUBMIT=''):
        'edit a template'
        if SUBMIT==FactoryDefaultString: return self.manage_default(REQUEST)
        if find(data,'\r'):
            data=join(split(data,'\r\n'),'\n\r')
            data=join(split(data,'\n\r'),'\n')
            
        if self.edited_source:
            self.edited_source=data
            self.cooked=self.cook()
        else:
            __traceback_info__=self.__class__
            newHTML=self.__class__()
            newHTML.__setstate__(self.__getstate__())
            newHTML.edited_source=data
            setattr(PARENTS[1],URL1[rfind(URL1,'/')+1:],newHTML)
        if REQUEST: return self.editConfirmation(self,REQUEST)
