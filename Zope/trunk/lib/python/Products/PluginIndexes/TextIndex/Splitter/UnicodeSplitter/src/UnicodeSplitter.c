#include "Python.h"

#define MAX_WORD 64		/* Words longer than MAX_WORD are stemmed */

typedef struct
{
    PyObject_HEAD
    PyObject *list;
    PyObject *synstop;
}
Splitter;
static
PyUnicodeObject *prepareString(PyUnicodeObject *o);

static PyObject * checkSynword(Splitter *self,PyObject *word)
{
    PyObject *value;
    PyObject *res;

    if (self->synstop) {
        value = PyDict_GetItem(self->synstop,word);
        if (value) {
            res = value;
        } else res = word;
    } res = word;

    return res;
}

static void
Splitter_dealloc(Splitter *self)
{
    Py_XDECREF(self->list);
    Py_XDECREF(self->synstop);
    PyMem_DEL(self);
}

static int
Splitter_length(Splitter *self)
{
    return PyList_Size(self->list);
}

static PyObject *
Splitter_concat(Splitter *self, PyObject *other)
{
    PyErr_SetString(PyExc_TypeError, "Cannot concatenate Splitters.");
    return NULL;
}

static PyObject *
Splitter_repeat(Splitter *self, long n)
{
    PyErr_SetString(PyExc_TypeError, "Cannot repeat Splitters.");
    return NULL;
}



static PyObject *
Splitter_item(Splitter *self, int i)
{
    PyObject *item=NULL;

    if (i >= PyList_Size(self->list)) {
        PyErr_SetString(PyExc_IndexError,"Splitter index out of range");
        return NULL;
    }

    item=PyList_GET_ITEM(self->list , i);
    Py_INCREF(item);

    return item;
}


static PyObject *
Splitter_indexes(Splitter *self, PyObject *args)
{
    int i=0;
    PyObject *word=NULL,*item=NULL,*r=NULL,*index=NULL;

    if (! (PyArg_ParseTuple(args,"O",&word))) return NULL;
    if (! (r=PyList_New(0))) return NULL;

    for (i=0;i<PyList_Size(self->list);i++) {
        item=PyList_GET_ITEM(self->list,i);

        if (PyUnicode_Compare(word,item)==0) {
            index=PyInt_FromLong(i);
            if(!index) return NULL;
            Py_INCREF(item);
            PyList_Append(r,index);
        }
    }

    return r;
}


static PyObject *
Splitter_slice(Splitter *self, int i, int j)
{
    PyErr_SetString(PyExc_TypeError, "Cannot slice Splitters.");
    return NULL;
}

static PySequenceMethods Splitter_as_sequence = {
    (inquiry)Splitter_length,        /*sq_length*/
    (binaryfunc)Splitter_concat,     /*sq_concat*/
    (intargfunc)Splitter_repeat,     /*sq_repeat*/
    (intargfunc)Splitter_item,       /*sq_item*/
    (intintargfunc)Splitter_slice,   /*sq_slice*/
    (intobjargproc)0,                    /*sq_ass_item*/
    (intintobjargproc)0,                 /*sq_ass_slice*/
};

static PyObject *
Splitter_pos(Splitter *self, PyObject *args)
{
    return Py_BuildValue("(ii)", 0,0);
}


static struct PyMethodDef Splitter_methods[] =
    {
        { "pos", (PyCFunction)Splitter_pos, 0,
            "pos(index) -- Return the starting and ending position of a token"
        },

        { "indexes", (PyCFunction)Splitter_indexes, METH_VARARGS,
          "indexes(word) -- Return al list of the indexes of word in the sequence",
        },
        { NULL, NULL }		/* sentinel */
    };


static PyObject *
Splitter_getattr(Splitter *self, char *name)
{
    return Py_FindMethod(Splitter_methods, (PyObject *)self, name);
}

static char SplitterType__doc__[] = "";

static PyTypeObject SplitterType = {
    PyObject_HEAD_INIT(NULL)
    0,                                 /*ob_size*/
    "Splitter",                    /*tp_name*/
    sizeof(Splitter),              /*tp_basicsize*/
    0,                                 /*tp_itemsize*/
    /* methods */
    (destructor)Splitter_dealloc,  /*tp_dealloc*/
    (printfunc)0,                      /*tp_print*/
    (getattrfunc)Splitter_getattr, /*tp_getattr*/
    (setattrfunc)0,                    /*tp_setattr*/
    (cmpfunc)0,                        /*tp_compare*/
    (reprfunc)0,                       /*tp_repr*/
    0,                                 /*tp_as_number*/
    &Splitter_as_sequence,         /*tp_as_sequence*/
    0,                                 /*tp_as_mapping*/
    (hashfunc)0,                       /*tp_hash*/
    (ternaryfunc)0,                    /*tp_call*/
    (reprfunc)0,                       /*tp_str*/

    /* Space for future expansion */
    0L,0L,0L,0L,
    SplitterType__doc__ /* Documentation string */
};


static int splitUnicodeString(Splitter *self,PyUnicodeObject *doc)
{

    PyObject *word,*synword;
    PyUnicodeObject * doc1;
    Py_UNICODE *s;

    int len = doc->length;
    int inside_word=0;
    int i=0;
    int start=0;

    if (! (doc1 = prepareString(doc))) {

        return 0;
    }

    s=doc1->str;

    self->list = PyList_New(0);

    do {
        register Py_UNICODE ch;

        ch = *s;
#ifdef DEBUG
        printf("%d %c %d\n",i,ch,ch);
        fflush(stdout);
#endif
        if (!inside_word) {
            if (Py_UNICODE_ISALPHA(ch)) {
                inside_word=1;
                start = i;
            }
        } else {

            if (!(Py_UNICODE_ISALNUM(ch) || ch=='/' || ch=='_' || ch=='-')) {
                inside_word = 0;

                word = PySequence_GetSlice((PyObject *)doc,start,i);
                if (word==NULL) {
                    Py_DECREF(doc1);
                    return 0;
                }

                // Stem word
                if (PyUnicode_GET_SIZE(word)>MAX_WORD) {
                    PyObject *tmpword=word;
                    tmpword = PySequence_GetSlice(word,0,MAX_WORD);
                    if (tmpword==NULL) {
                        Py_DECREF(doc1);
                        return 0;
                    }

                    Py_DECREF(word);

                    word = tmpword;
                }

                synword = checkSynword(self,word);
                if (synword != Py_None) {
                    PyList_Append(self->list,synword);
                }

                Py_DECREF(word);

                start =  0;
#ifdef DEBUG
                PyObject_Print(word,stdout,0);
                fflush(stdout);
#endif
            }
        }

        s++;

    } while(++i < len);

    if (inside_word) {
        word = PySequence_GetSlice((PyObject *)doc,start,i);
        if (word==NULL) {
            Py_DECREF(doc1);
            return 0;
        }

        // Stem word
        if (PyUnicode_GET_SIZE(word)>MAX_WORD) {
            word = PySequence_GetSlice(word,0,MAX_WORD);
            if (word==NULL) {
                Py_DECREF(doc1);
                return 0;
            }

        }

        synword = checkSynword(self,word);
        if (synword != Py_None) {
            PyList_Append(self->list,synword);
        } else Py_DECREF(synword);

        Py_DECREF(word);
    }

#ifdef DEBUG
    PyObject_Print(self->list,stdout,0);
    fflush(stdout);
#endif

    Py_DECREF(doc1);
    return 1;
}


static
void fixlower(PyUnicodeObject *self)
{
    int len = self->length;
    Py_UNICODE *s = self->str;

    while (len-- > 0) {
        register Py_UNICODE ch;

        ch = Py_UNICODE_TOLOWER(*s);
        if (ch != *s) *s = ch;
        s++;
    }
}


static
PyUnicodeObject *prepareString(PyUnicodeObject *o)

{
    PyUnicodeObject *u;

    u = (PyUnicodeObject*) PyUnicode_FromUnicode(NULL, o->length);
    if (u == NULL) return NULL;

    Py_UNICODE_COPY(u->str, o->str, o->length);
    fixlower(u);

    return  u;
}

static char *splitter_args[]={"encoding",NULL};


static PyObject *
get_Splitter(PyObject *modinfo, PyObject *args,PyObject *keywds)
{
    Splitter *self=NULL;
    PyObject *doc=NULL, *unicodedoc=NULL,*synstop=NULL;
    char *encoding = "latin1";

    if (! (self = PyObject_NEW(Splitter, &SplitterType))) return NULL;
    if (! (PyArg_ParseTupleAndKeywords(args,keywds,"O|Os",splitter_args,&doc,&synstop,&encoding))) return NULL;

#ifdef DEBUG
    puts("got text");
    PyObject_Print(doc,stdout,0);
    fflush(stdout);
#endif

    if (PyString_Check(doc)) {

        unicodedoc = PyUnicode_FromEncodedObject(doc,encoding,"strict");
        if (unicodedoc ==NULL) {
            PyErr_SetString(PyExc_UnicodeError, "Problem converting encoded string");
            return NULL;
        }

    } else if( PyUnicode_Check(doc)) {
        unicodedoc = doc;
        Py_INCREF(unicodedoc);

    } else {
        PyErr_SetString(PyExc_TypeError, "first argument is neither string nor unicode.");
        return NULL;
    }



    if (synstop) {
        self->synstop = synstop;
        Py_INCREF(synstop);
    } else  self->synstop=NULL;

    if (! (splitUnicodeString(self,(PyUnicodeObject *)unicodedoc))) {
        goto err;
    }


    Py_DECREF(unicodedoc);
    return (PyObject*)self;

err:
    Py_DECREF(self);
    Py_DECREF(unicodedoc);

    return NULL;
}

static struct PyMethodDef Splitter_module_methods[] =
    {
        { "UnicodeSplitter", (PyCFunction)get_Splitter, METH_VARARGS|METH_KEYWORDS,
            "UnicodeSplitter(doc[,synstop][,encoding='latin1']) -- Return a word splitter"
        },
        { NULL, NULL }
    };

static char Splitter_module_documentation[] =
    "Parse source (unicode) string into sequences of words\n"
    "\n"
    "for use in an inverted index\n"
    "\n"
    "$Id: UnicodeSplitter.c,v 1.6 2001/10/17 19:11:09 andreasjung Exp $\n"
    ;


void
initUnicodeSplitter(void)
{
    PyObject *m, *d;
    char *rev="$Revision: 1.6 $";

    /* Create the module and add the functions */
    m = Py_InitModule4("UnicodeSplitter", Splitter_module_methods,
                       Splitter_module_documentation,
                       (PyObject*)NULL,PYTHON_API_VERSION);

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "__version__",
                         PyString_FromStringAndSize(rev+11,strlen(rev+11)-2));

    if (PyErr_Occurred()) Py_FatalError("can't initialize module Splitter");
}
