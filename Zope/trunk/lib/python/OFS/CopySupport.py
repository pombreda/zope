"""Copy interface"""

__version__='$Revision: 1.1 $'[11:-2]

import Globals, Moniker, rPickle
from cPickle import loads, dumps
from urllib import quote, unquote
from App.Dialogs import MessageDialog


rPickle.register('OFS.Moniker', 'Moniker', Moniker.Moniker)



class CopyContainer:
    # Interface for containerish objects which allow
    # objects to be copied into them.

    def _getMoniker(self):
        # Ask an object to return a moniker for itself.
	return Moniker.Moniker(self)

    pasteDialog=Globals.HTMLFile('OFS/pasteDialog')

    def pasteFromClipboard(self,clip_id='',clip_data='',REQUEST=None):
        """ """
	if not clip_data: return eNoData

	try:    moniker=rPickle.loads(unquote(clip_data))
	except: return eInvalid

	if not clip_id:
	    return self.pasteDialog(self,REQUEST,bad=0,moniker=(moniker,))

	try:    self._checkId(clip_id)
	except: return self.pasteDialog(self,REQUEST,bad=1,moniker=(moniker,))

	try:    obj=moniker.bind()
	except: return eNotFound

	# Acquire roles from new environment
	try:    del obj.__roles__
	except: pass

	obj=obj._getCopy(self)
        obj._setId(clip_id)
	self._setObject(clip_id, obj)
	return self.manage_main(self, REQUEST)





class CopySource:
    # Interface for objects which allow themselves to be copied.

    def _getMoniker(self):
        # Ask an object to return a moniker for itself.
	return Moniker.Moniker(self)

    def _getCopy(self, container):
	# Ask an object for a new copy of itself.
	return loads(dumps(self))

    def _setId(self, id):
	# Called to set the new id of a copied object.
	self.id=id

    def copyToClipboard(self, REQUEST):
        """ """
	# Set a cookie containing pickled moniker
	try:    moniker=self._getMoniker()
	except: return eNotSupported
	REQUEST['RESPONSE'].setCookie('clip_data',
			    quote(dumps(moniker)),
			    path='/',
			    expires='Friday, 31-Dec-99 23:59:59 GMT')




# Predefined errors

eNoData=Globals.MessageDialog(
        title='No Data',
	message='No clipboard data to be pasted',
	action ='./manage_main',)

eInvalid=Globals.MessageDialog(
	 title='Clipboard Error',
	 message='Clipboard data could not be read ' \
		 'or is not supported in this installation',
	 action ='./manage_main',)

eNotFound=Globals.MessageDialog(
	  title='Clipboard Error',
	  message='The item referenced by the ' \
	          'clipboard data was not found',
	  action ='./manage_main',)

eNotSupported=Globals.MessageDialog(
	      title='Not Supported',
	      message='Operation not supported for the selected item',
	      action ='./manage_main',)



