/*

  $Id: Acquisition.c,v 1.1 1997/02/17 15:05:40 jim Exp $

  Acquisition Wrappers -- Implementation of acquisition through wrappers


     Copyright 

       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
       rights reserved.  Copyright in this software is owned by DCLC,
       unless otherwise indicated. Permission to use, copy and
       distribute this software is hereby granted, provided that the
       above copyright notice appear in all copies and that both that
       copyright notice and this permission notice appear. Note that
       any product, process or technology described in this software
       may be the subject of other Intellectual Property rights
       reserved by Digital Creations, L.C. and are not licensed
       hereunder.

     Trademarks 

       Digital Creations & DCLC, are trademarks of Digital Creations, L.C..
       All other trademarks are owned by their respective companies. 

     No Warranty 

       The software is provided "as is" without warranty of any kind,
       either express or implied, including, but not limited to, the
       implied warranties of merchantability, fitness for a particular
       purpose, or non-infringement. This software could include
       technical inaccuracies or typographical errors. Changes are
       periodically made to the software; these changes will be
       incorporated in new editions of the software. DCLC may make
       improvements and/or changes in this software at any time
       without notice.

     Limitation Of Liability 

       In no event will DCLC be liable for direct, indirect, special,
       incidental, economic, cover, or consequential damages arising
       out of the use of or inability to use this software even if
       advised of the possibility of such damages. Some states do not
       allow the exclusion or limitation of implied warranties or
       limitation of liability for incidental or consequential
       damages, so the above limitation or exclusion may not apply to
       you.

    If you have questions regarding this software,
    contact:
   
      Jim Fulton, jim@digicool.com
      Digital Creations L.C.  
   
      (540) 371-6909


  Full description

  $Log: Acquisition.c,v $
  Revision 1.1  1997/02/17 15:05:40  jim
  *** empty log message ***


*/
#include "ExtensionClass.h"

static void
PyVar_Assign(PyObject **v,  PyObject *e)
{
  Py_XDECREF(*v);
  *v=e;
}

#define ASSIGN(V,E) PyVar_Assign(&(V),(E))
#define UNLESS(E) if(!(E))
#define UNLESS_ASSIGN(V,E) ASSIGN(V,E); UNLESS(V)

static PyObject *py__add__, *py__sub__, *py__mul__, *py__div__,
  *py__mod__, *py__pow__, *py__divmod__, *py__lshift__, *py__rshift__,
  *py__and__, *py__or__, *py__xor__, *py__coerce__, *py__neg__,
  *py__pos__, *py__abs__, *py__nonzero__, *py__inv__, *py__int__,
  *py__long__, *py__float__, *py__oct__, *py__hex__,
  *py__getitem__, *py__setitem__, *py__delitem__,
  *py__getslice__, *py__setslice__, *py__delslice__,
  *py__concat__, *py__repeat__, *py__len__, *py__of__, *py__call__,
  *py__repr__, *py__str__;

static void
init_py_names()
{
#define INIT_PY_NAME(N) py ## N = PyString_FromString(#N)
  INIT_PY_NAME(__add__);
  INIT_PY_NAME(__sub__);
  INIT_PY_NAME(__mul__);
  INIT_PY_NAME(__div__);
  INIT_PY_NAME(__mod__);
  INIT_PY_NAME(__pow__);
  INIT_PY_NAME(__divmod__);
  INIT_PY_NAME(__lshift__);
  INIT_PY_NAME(__rshift__);
  INIT_PY_NAME(__and__);
  INIT_PY_NAME(__or__);
  INIT_PY_NAME(__xor__);
  INIT_PY_NAME(__coerce__);
  INIT_PY_NAME(__neg__);
  INIT_PY_NAME(__pos__);
  INIT_PY_NAME(__abs__);
  INIT_PY_NAME(__nonzero__);
  INIT_PY_NAME(__inv__);
  INIT_PY_NAME(__int__);
  INIT_PY_NAME(__long__);
  INIT_PY_NAME(__float__);
  INIT_PY_NAME(__oct__);
  INIT_PY_NAME(__hex__);
  INIT_PY_NAME(__getitem__);
  INIT_PY_NAME(__setitem__);
  INIT_PY_NAME(__delitem__);
  INIT_PY_NAME(__getslice__);
  INIT_PY_NAME(__setslice__);
  INIT_PY_NAME(__delslice__);
  INIT_PY_NAME(__concat__);
  INIT_PY_NAME(__repeat__);
  INIT_PY_NAME(__len__);
  INIT_PY_NAME(__of__);
  INIT_PY_NAME(__call__);
  INIT_PY_NAME(__repr__);
  INIT_PY_NAME(__str__);
  
#undef INIT_PY_NAME
}

static PyObject *
CallMethodO(PyObject *self, PyObject *name,
		     PyObject *args, PyObject *kw)
{
  if(! args && PyErr_Occurred()) return NULL;
  UNLESS(name=PyObject_GetAttr(self,name)) return NULL;
  ASSIGN(name,PyEval_CallObjectWithKeywords(name,args,kw));
  if(args) Py_DECREF(args);
  return name;
}

#define Build Py_BuildValue

/* Declarations for objects of type Wrapper */

typedef struct {
  PyObject_HEAD
  PyObject *obj;
  PyObject *container;
} Wrapper;

staticforward PyExtensionClass Wrappertype;

static PyObject *
Wrapper__init__(Wrapper *self, PyObject *args)
{
  PyObject *obj, *container;

  UNLESS(PyArg_Parse(args,"(OO)",&obj,&container)) return NULL;
  Py_INCREF(obj);
  Py_INCREF(container);
  self->obj=obj;
  self->container=container;
  Py_INCREF(Py_None);
  return Py_None;
}

/* ---------------------------------------------------------------- */

static struct PyMethodDef Wrapper_methods[] = {
  {"__init__", (PyCFunction)Wrapper__init__, 0,
   "Initialize an Acquirer Wrapper"},
  {NULL,		NULL}		/* sentinel */
};

/* ---------- */

static Wrapper *
newWrapper(PyObject *obj, PyObject *container)
{
  Wrapper *self;
  
  UNLESS(self = PyObject_NEW(Wrapper, (PyTypeObject*)&Wrappertype)) return NULL;
  Py_INCREF(obj);
  Py_INCREF(container);
  self->obj=obj;
  self->container=container;
  return self;
}


static void
Wrapper_dealloc(Wrapper *self)     
{
  Py_DECREF(self->obj);
  Py_DECREF(self->container);
  PyMem_DEL(self);
}

static PyObject *
Wrapper_getattro(Wrapper *self, PyObject *oname)
{
  PyObject *r;
  char *name;

  if(self->obj && (r=PyObject_GetAttr(self->obj,oname)))
    {
      if(r->ob_type==(PyTypeObject*)&Wrappertype)
	{
	  if(r->ob_refcnt==1)
	    {
	      Py_INCREF(self);
	      ASSIGN(((Wrapper*)r)->container,(PyObject*)self);
	    }
	  else
	    ASSIGN(r,(PyObject*)newWrapper(((Wrapper*)r)->obj,
					   (PyObject*)self));
	}
      else if(PyECMethod_Check(r) && PyECMethod_Self(r)==self->obj)
	ASSIGN(r,PyECMethod_New(r,(PyObject*)self));
      else if(has__of__(r))
	ASSIGN(r,CallMethodO(r,py__of__,Build("O", self), NULL));
      return r;
    }
  if(self->obj) PyErr_Clear();

  name=PyString_AsString(oname);

  if(self->container && *name != '_') 
    {
      if(r=PyObject_GetAttr(self->container,oname))
	return r;
      PyErr_Clear();
    }

  if(*name++=='a' && *name++=='q' && *name++=='_')
    {
      if(strcmp(name,"parent")==0)
	{
	  if(self->container) r=self->container;
	  else r=Py_None;
	  Py_INCREF(r);
	  return r;
	}
      if(strcmp(name,"self")==0)
	{
	  if(self->obj) r=self->obj;
	  else r=Py_None;
	  Py_INCREF(r);
	  return r;
	}
    }

  if(*name++=='_' && strcmp(name,"_init__")==0)
    return Py_FindAttr((PyObject*)self,oname);

  PyErr_SetObject(PyExc_AttributeError,oname);
  return NULL;
}

static int
Wrapper_setattro(Wrapper *self, PyObject *name, PyObject *v)
{
  if(v && v->ob_type==(PyTypeObject*)&Wrappertype) v=((Wrapper*)v)->obj;
  return PyObject_SetAttr(self->obj, name, v);
}

static int
Wrapper_compare(Wrapper *v, Wrapper *w)
{
  return PyObject_Compare(v->obj,w->obj);
}

static PyObject *
Wrapper_repr(Wrapper *self)
{
  PyObject *r;

  if(r=PyObject_GetAttr((PyObject*)self,py__repr__))
    {
      ASSIGN(r,PyObject_CallFunction(r,NULL,NULL));
      return r;
    }
  else
    {
      PyErr_Clear();
      return PyObject_Repr(self->obj);
    }
}

static PyObject *
Wrapper_str(Wrapper *self)
{
  PyObject *r;

  if(r=PyObject_GetAttr((PyObject*)self,py__str__))
    {
      ASSIGN(r,PyObject_CallFunction(r,NULL,NULL));
      return r;
    }
  else
    {
      PyErr_Clear();
      return PyObject_Str(self->obj);
    }
}

static long
Wrapper_hash(Wrapper *self)
{
  return PyObject_Hash(self->obj);
}

static PyObject *
Wrapper_call(Wrapper *self, PyObject *args, PyObject *kw)
{
  Py_INCREF(args);
  return CallMethodO((PyObject*)self,py__call__,args,kw);
}



/* Code to handle accessing Wrapper objects as sequence objects */

static int
Wrapper_length(Wrapper *self)
{
  long l;
  PyObject *r;

  UNLESS(r=CallMethodO((PyObject*)self,py__len__,NULL,NULL))  return -1;
  l=PyInt_AsLong(r);
  Py_DECREF(r);
  return l;
}

static PyObject *
Wrapper_concat(Wrapper *self, PyObject *bb)
{
  return CallMethodO((PyObject*)self,py__concat__,Build("(O)", bb) ,NULL);
}

static PyObject *
Wrapper_repeat(Wrapper *self, int  n)
{
  return CallMethodO((PyObject*)self,py__repeat__,Build("(i)", n),NULL);
}

static PyObject *
Wrapper_item(Wrapper *self, int  i)
{
  return CallMethodO((PyObject*)self,py__getitem__, Build("(i)", i),NULL);
}

static PyObject *
Wrapper_slice(Wrapper *self, int  ilow, int  ihigh)
{
  return CallMethodO((PyObject*)self,py__getslice__,
		     Build("(ii)", ilow, ihigh),NULL);
}

static int
Wrapper_ass_item(Wrapper *self, int  i, PyObject *v)
{
  if(v)
    {
      UNLESS(v=CallMethodO((PyObject*)self,py__setitem__,
			   Build("(iO)", i, v),NULL))
	return -1;
    }
  else
    {
      UNLESS(v=CallMethodO((PyObject*)self,py__delitem__,
			   Build("(iO)", i),NULL))
	return -1;
    }
  Py_DECREF(v);
  return 0;
}

static int
Wrapper_ass_slice(Wrapper *self, int  ilow, int  ihigh, PyObject *v)
{
  if(v)
    {
      UNLESS(v=CallMethodO((PyObject*)self,py__setslice__,
			   Build("(iiO)", ilow, ihigh, v),NULL))
	return -1;
    }
  else
    {
      UNLESS(v=CallMethodO((PyObject*)self,py__delslice__,
			   Build("(ii)", ilow, ihigh),NULL))
	return -1;
    }
  Py_DECREF(v);
  return 0;
}

static PySequenceMethods Wrapper_as_sequence = {
	(inquiry)Wrapper_length,		/*sq_length*/
	(binaryfunc)Wrapper_concat,		/*sq_concat*/
	(intargfunc)Wrapper_repeat,		/*sq_repeat*/
	(intargfunc)Wrapper_item,		/*sq_item*/
	(intintargfunc)Wrapper_slice,		/*sq_slice*/
	(intobjargproc)Wrapper_ass_item,	/*sq_ass_item*/
	(intintobjargproc)Wrapper_ass_slice,	/*sq_ass_slice*/
};

/* -------------------------------------------------------------- */

/* Code to access Wrapper objects as mappings */

static PyObject *
Wrapper_subscript(Wrapper *self, PyObject *key)
{
  return CallMethodO((PyObject*)self,py__getitem__,Build("(O)", key),NULL);
}

static int
Wrapper_ass_sub(Wrapper *self, PyObject *key, PyObject *v)
{
  if(v)
    {
      UNLESS(v=CallMethodO((PyObject*)self,py__setitem__,
			   Build("(OO)", key, v),NULL))
	return -1;
    }
  else
    {
      UNLESS(v=CallMethodO((PyObject*)self,py__delitem__,
			   Build("(O)", key),NULL))
	return -1;
    }
  Py_XDECREF(v);
  return 0;
}

static PyMappingMethods Wrapper_as_mapping = {
  (inquiry)Wrapper_length,		/*mp_length*/
  (binaryfunc)Wrapper_subscript,	/*mp_subscript*/
  (objobjargproc)Wrapper_ass_sub,	/*mp_ass_subscript*/
};

/* -------------------------------------------------------- */

static char Wrappertype__doc__[] = 
""
;

static PyExtensionClass Wrappertype = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "AcquirerWrapper",			/*tp_name*/
  sizeof(Wrapper),       		/*tp_basicsize*/
  0,					/*tp_itemsize*/
  /* methods */
  (destructor)Wrapper_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)Wrapper_compare,    		/*tp_compare*/
  (reprfunc)Wrapper_repr,      		/*tp_repr*/
  0,					/*tp_as_number*/
  &Wrapper_as_sequence,			/*tp_as_sequence*/
  &Wrapper_as_mapping,			/*tp_as_mapping*/
  (hashfunc)Wrapper_hash,      		/*tp_hash*/
  (ternaryfunc)Wrapper_call,		/*tp_call*/
  (reprfunc)Wrapper_str,       		/*tp_str*/
  (getattrofunc)Wrapper_getattro,	/*tp_getattr with object key*/
  (setattrofunc)Wrapper_setattro,      	/*tp_setattr with object key*/

  /* Space for future expansion */
  0L,0L,
  Wrappertype__doc__, /* Documentation string */
  METHOD_CHAIN(Wrapper_methods),
  EXTENSIONCLASS_BINDABLE_FLAG,
};

/* End of code for Wrapper objects */
/* -------------------------------------------------------- */


/* List of methods defined in the module */

static struct PyMethodDef Wrap_methods[] = {
  
  {NULL,		NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initWrap) */

static char Wrap_module_documentation[] = 
""
;

static PyObject *
acquire_of(PyObject *self, PyObject *args)
{
  PyObject *inst;

  UNLESS(PyArg_Parse(args,"O",&inst)) return NULL;

  UNLESS(PyExtensionInstance_Check(inst))
    {
      PyErr_SetString(PyExc_TypeError,
		      "attempt to wrap extension method using an object that\n"
		      "is not an extension class instance.");
      return NULL;
    }

  return (PyObject*)newWrapper(self,args);
}

struct PyMethodDef Acquirer_methods[] = {
  {"__of__",(PyCFunction)acquire_of,0,""},
  
  {NULL,		NULL}		/* sentinel */
};

static struct PyMethodDef methods[] = {{NULL,	NULL}};


void
initAcquisition()
{
  PyObject *m, *d;
  PURE_MIXIN_CLASS(Acquirer,
	"Base class for objects that acquire attributes from containers\n"
	, Acquirer_methods)

    /* Create the module and add the functions */
    m = Py_InitModule4("Acquisition", methods,
		       "",
		       (PyObject*)NULL,PYTHON_API_VERSION);

  d = PyModule_GetDict(m);
  init_py_names();
  PyExtensionClass_Export(d,"Acquirer",AcquirerType);
  PyExtensionClass_Export(d,"Wrapper",Wrappertype);

  CHECK_FOR_ERRORS("can't initialize module Acquisition");
}
