=============
Z3C Templates
=============

This package allows us to separate the registration of the view code and the
layout.

A template is used for separate the HTML part from a view. This is done in
z3 via a page templates. Such page template are implemented in the view,
registered included in a page directive etc. But they do not use the adapter
pattern which makes it hard to replace existing templates.

Another part of template is, that they normaly separate one part presenting
content from a view and another part offer a layout used by the content
template.

How can this package make it simpler to use templates?

Templates can be registered as adapters adapting context, request where the
context is a view implementation. Such a template get adapted from the view
if the template is needed. This adaption makes it very pluggable and modular.

We offer two base template directive for register content producing templates
and layout producing tempaltes. This is most the time enough but you also
can register different type of templates using a specific interface. This
could be usefull if your view implementation needs to separate HTMl in
more then one template. Now let's take a look how we an use this templates.


Content template
----------------

First let's show how we use a template for produce conent from a view:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> contentTemplate = os.path.join(temp_dir, 'contentTemplate.pt')
  >>> open(contentTemplate, 'w').write('''<div>demo content</div>''')

And register a view class implementing a interface:

  >>> import zope.interface
  >>> from z3c.template import interfaces
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from zope.publisher.browser import BrowserPage

  >>> class IMyView(zope.interface.Interface):
  ...     pass
  >>> class MyView(BrowserPage):
  ...     zope.interface.implements(IMyView)
  ...     template = None
  ...     def render(self):
  ...         if self.template is None:
  ...             template = zope.component.getMultiAdapter(
  ...                 (self, self.request), interfaces.IContentTemplate)
  ...             return template(self)
  ...         return self.template()

Let's call the view and check the output:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> view = MyView(root, request)

Since the template is not yet registered, rendering the view will fail:

  >>> print view.render()
  Traceback (most recent call last):
  ...
  ComponentLookupError: ......

Let's now register the template (commonly done using ZCML):

  >>> from zope import component
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from z3c.template.template import TemplateFactory

The template factory allows us to create a ViewPageTeplateFile instance.

  >>> factory = TemplateFactory(contentTemplate, 'text/html')

We register the factory on a view interface and a layer.

  >>> component.provideAdapter(
  ...     factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...     interfaces.IContentTemplate)
  >>> template = component.getMultiAdapter((view, request),
  ...     interfaces.IPageTemplate)
  >>> template
  <zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile object at ...>

Now that we have a registered layout template for the default layer we can
call our view again.

  >>> print view.render()
  <div>demo content</div>

Now we register a new template on the specific interface of our view.

  >>> myTemplate = os.path.join(temp_dir, 'myTemplate.pt')
  >>> open(myTemplate, 'w').write('''<div>My content</div>''')
  >>> factory = TemplateFactory(myTemplate, 'text/html')
  >>> component.provideAdapter(
  ...     factory,
  ...     (IMyView, IDefaultBrowserLayer), interfaces.IContentTemplate)
  >>> print view.render()
  <div>My content</div>

It is possible to provide the template directly.

We create a new template.

  >>> viewContent = os.path.join(temp_dir, 'viewContent.pt')
  >>> open(viewContent, 'w').write('''<div>view content</div>''')

and a view:

  >>> from zope.app.pagetemplate import ViewPageTemplateFile
  >>> class MyViewWithTemplate(BrowserPage):
  ...     zope.interface.implements(IMyView)
  ...     template = ViewPageTemplateFile(viewContent)
  ...     def render(self):
  ...         if self.template is None:
  ...             template = zope.component.getMultiAdapter(
  ...                 (self, self.request), interfaces.IContentTemplate)
  ...             return template(self)
  ...         return self.template()
  >>> contentView = MyViewWithTemplate(root, request)

If we render this view we get the implemented layout template and not the
registered one.

  >>> print contentView.render()
  <div>view content</div>


Layout template
---------------

First we nee to register a new view class calling a layout template. Note,
that this view uses the __call__ method for invoke a layout template:

  >>> class ILayoutView(zope.interface.Interface):
  ...     pass
  >>> class LayoutView(BrowserPage):
  ...     zope.interface.implements(ILayoutView)
  ...     layout = None
  ...     def __call__(self):
  ...         if self.layout is None:
  ...             layout = zope.component.getMultiAdapter(
  ...                 (self, self.request), interfaces.ILayoutTemplate)
  ...             return layout(self)
  ...         return self.layout()
  >>> view2 = LayoutView(root, request)

Define and register a new layout template:

  >>> layoutTemplate = os.path.join(temp_dir, 'layoutTemplate.pt')
  >>> open(layoutTemplate, 'w').write('''<div>demo layout</div>''')
  >>> factory = TemplateFactory(layoutTemplate, 'text/html')

We register the template factory on a view interface and a layer providing the
ILayoutTemplate interface.

  >>> component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...      interfaces.ILayoutTemplate)
  >>> layout = component.getMultiAdapter(
  ...     (view2, request), interfaces.ILayoutTemplate)
  >>> layout
  <zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile ...>

Now that we have a registered layout template for the default layer we can
call our view again.

  >>> print view2()
  <div>demo layout</div>

Now we register a new layout template on the specific interface of our view.

  >>> myLayout = os.path.join(temp_dir, 'myLayout.pt')
  >>> open(myLayout, 'w').write('''<div>My layout</div>''')
  >>> factory = TemplateFactory(myLayout, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (ILayoutView, IDefaultBrowserLayer),
  ...      interfaces.ILayoutTemplate)
  >>> print view2()
  <div>My layout</div>

It is possible to provide the layout template directly.

We create a new template.

  >>> viewLayout = os.path.join(temp_dir, 'viewLayout.pt')
  >>> open(viewLayout, 'w').write('''<div>view layout</div>''')

  >>> class LayoutViewWithLayoutTemplate(BrowserPage):
  ...     zope.interface.implements(ILayoutView)
  ...     layout = ViewPageTemplateFile(viewLayout)
  ...     def __call__(self):
  ...         if self.layout is None:
  ...             layout = zope.component.getMultiAdapter((self, self.request),
  ...                 interfaces.ILayoutTemplate)
  ...             return layout(self)
  ...         return self.layout()
  >>> layoutView = LayoutViewWithLayoutTemplate(root, request)

If we render this view we get the implemented layout template and not the
registered one.

  >>> print layoutView()
  <div>view layout</div>


Since we return the layout template in the sample views above, how can we get
the content from the used view? This is not directly a part of this package
but let's show some pattern were can be used for render content in a used
layout template. Note, since we offer to register each layout template for
a specific view, you can always very selectiv this layout pattern. This means
you can use the defualt z3 macro based layout registration in combination with
this layout concept if you register a own layout template.

The simplest concept is calling the content from the view in the layout
template is to call it from a method. Let's define a view providing a layout
template and offer a method for call content.

  >>> class IFullView(zope.interface.Interface):
  ...     pass

  >>> class FullView(BrowserPage):
  ...     zope.interface.implements(IFullView)
  ...     layout = None
  ...     def render(self):
  ...         return u'rendered content'
  ...     def __call__(self):
  ...         if self.layout is None:
  ...             layout = zope.component.getMultiAdapter((self, self.request),
  ...                 interfaces.ILayoutTemplate)
  ...             return layout(self)
  ...         return self.layout()
  >>> completeView = FullView(root, request)

Now define a layout for the view and register them:

  >>> completeLayout = os.path.join(temp_dir, 'completeLayout.pt')
  >>> open(completeLayout, 'w').write('''
  ...   <div tal:content="view/render">
  ...     Full layout
  ...   </div>
  ... ''')

  >>> factory = TemplateFactory(completeLayout, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (IFullView, IDefaultBrowserLayer), interfaces.ILayoutTemplate)

Now let's see if the layout template can call the content via calling render
on the view:

  >>> print completeView.__call__()
  <div>rendered content</div>


Content and Layout
------------------

Now let's show how we combine this two templates in a real use case:

  >>> class IDocumentView(zope.interface.Interface):
  ...     pass

  >>> class DocumentView(BrowserPage):
  ...     zope.interface.implements(IDocumentView)
  ...     template = None
  ...     layout = None
  ...     attr = None
  ...     def update(self):
  ...         self.attr = u'content updated'
  ...     def render(self):
  ...         if self.template is None:
  ...             template = zope.component.getMultiAdapter(
  ...                 (self, self.request), IPageTemplate)
  ...             return template(self)
  ...         return self.template()
  ...     def __call__(self):
  ...         self.update()
  ...         if self.layout is None:
  ...             layout = zope.component.getMultiAdapter((self, self.request),
  ...                 interfaces.ILayoutTemplate)
  ...             return layout(self)
  ...         return self.layout()

Define and register a content template...

  >>> template = os.path.join(temp_dir, 'template.pt')
  >>> open(template, 'w').write('''
  ...   <div tal:content="view/attr">
  ...     here comes the value of attr
  ...   </div>
  ... ''')

  >>> factory = TemplateFactory(template, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (IDocumentView, IDefaultBrowserLayer), IPageTemplate)

and define and register a layout template:

  >>> layout = os.path.join(temp_dir, 'layout.pt')
  >>> open(layout, 'w').write('''
  ... <html>
  ...   <body>
  ...     <div tal:content="structure view/render">
  ...       here comes the rendered content
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

  >>> factory = TemplateFactory(layout, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (IDocumentView, IDefaultBrowserLayer), interfaces.ILayoutTemplate)

Now call the view and check the result:

  >>> documentView = DocumentView(root, request)
  >>> print documentView()
  <html>
    <body>
      <div>
        <div>content updated</div>
      </div>
    </body>
  </html>


Macros
------

Use of macros.

  >>> macroTemplate = os.path.join(temp_dir, 'macroTemplate.pt')
  >>> open(macroTemplate, 'w').write('''
  ...   <metal:block define-macro="macro1">
  ...     <div>macro1</div>
  ...   </metal:block>
  ...   <metal:block define-macro="macro2">
  ...     <div>macro2</div>
  ...   </metal:block>
  ...   ''')

  >>> factory = TemplateFactory(macroTemplate, 'text/html', 'macro1')
  >>> print factory(view, request)()
  <div>macro1</div>


Why didn't we use named templates from the ``zope.formlib`` package?

While named templates allow us to separate the view code from the template
registration, they are not registrable for a particular layer making it
impossible to implement multiple skins using named templates.


Use case ``simple template``
----------------------------

And for the simplest possible use we provide a hook for call registered
templates. Such page templates can get called with the getPageTemplate method
and return a registered bound ViewTemplate a la ViewPageTemplateFile or
NamedTemplate.

The getViewTemplate allows us to use the new template registration
system with all existing implementations such as `zope.formlib` and
`zope.viewlet`.

  >>> from z3c.template.template import getPageTemplate
  >>> class IUseOfViewTemplate(zope.interface.Interface):
  ...     pass
  >>> class UseOfViewTemplate(object):
  ...     zope.interface.implements(IUseOfViewTemplate)
  ...
  ...     template = getPageTemplate()
  ...
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request

By defining the "template" property as a "RegisteredPageTemplate" a lookup for
a registered template is done when it is called. Also notice that it is no
longer necessary to derive the view from BaseView!

  >>> simple = UseOfViewTemplate(root, request)
  >>> print simple.template()
  <div>demo content</div>

Because the demo template was registered for any ("None") interface we see the
demo template when rendering our new view. We register a new template
especially for the new view. Also not that the "macroTemplate" has been
created earlier in this test.

  >>> factory = TemplateFactory(contentTemplate, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (IUseOfViewTemplate, IDefaultBrowserLayer), IPageTemplate)
  >>> print simple.template()
  <div>demo content</div>


Use case ``template by interface``
----------------------------------

Templates can also get registered on different interfaces then IPageTemplate
or ILayoutTemplate.

  >>> from z3c.template.template import getViewTemplate
  >>> class IMyTemplate(zope.interface.Interface):
  ...     """My custom tempalte marker."""

  >>> factory = TemplateFactory(contentTemplate, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer), IMyTemplate)

Now define a view using such a custom template registration:

  >>> class IMyTemplateView(zope.interface.Interface):
  ...     pass
  >>> class MyTemplateView(object):
  ...     zope.interface.implements(IMyTemplateView)
  ...
  ...     template = getViewTemplate(IMyTemplate)
  ...
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request

  >>> myTempalteView = MyTemplateView(root, request)
  >>> print myTempalteView.template()
  <div>demo content</div>


Use case ``named template``
----------------------------------

Templates can also get registered on names. In this expample we use a named
template combined with a custom template marker interface.

  >>> class IMyNamedTemplate(zope.interface.Interface):
  ...     """My custom template marker."""

  >>> factory = TemplateFactory(contentTemplate, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer), IMyNamedTemplate,
  ...     name='my template')

Now define a view using such a custom named template registration:

  >>> class IMyNamedTemplateView(zope.interface.Interface):
  ...     pass
  >>> class MyNamedTemplateView(object):
  ...     zope.interface.implements(IMyNamedTemplateView)
  ...
  ...     template = getViewTemplate(IMyNamedTemplate, 'my template')
  ...
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request

  >>> myNamedTempalteView = MyNamedTemplateView(root, request)
  >>> print myNamedTempalteView.template()
  <div>demo content</div>


Use case ``named layout template``
----------------------------------

We can also register a new layout template by name and use it in a view:

  >>> from z3c.template.template import getLayoutTemplate

  >>> editLayout = os.path.join(temp_dir, 'editLayout.pt')
  >>> open(editLayout, 'w').write('''
  ...   <div>Edit layout</div>
  ...   <div tal:content="view/render">content</div>
  ... ''')
  >>> factory = TemplateFactory(editLayout, 'text/html')
  >>> component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...      interfaces.ILayoutTemplate, name='edit')

Now define a view using such a custom named template registration:

  >>> class MyEditView(BrowserPage):
  ...
  ...     layout = getLayoutTemplate('edit')
  ...
  ...     def render(self):
  ...         return u'edit content'
  ...
  ...     def __call__(self):
  ...         if self.layout is None:
  ...             layout = zope.component.getMultiAdapter((self, self.request),
  ...                 interfaces.ILayoutTemplate)
  ...             return layout(self)
  ...         return self.layout()

  >>> myEditView = MyEditView(root, request)
  >>> print myEditView()
  <div>Edit layout</div>
  <div>edit content</div>


Cleanup
-------

  >>> import shutil
  >>> shutil.rmtree(temp_dir)


Pagelet
-------

See z3c.pagelet for another template based layout genering implementation.
