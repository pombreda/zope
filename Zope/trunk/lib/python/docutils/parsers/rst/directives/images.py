# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 1.5 $
# Date: $Date: 2003/11/30 15:06:06 $
# Copyright: This module has been placed in the public domain.

"""
Directives for figures and simple images.
"""

__docformat__ = 'reStructuredText'


import sys
from docutils import nodes, utils
from docutils.parsers.rst import directives

try:
    import Image                        # PIL
except ImportError:
    Image = None

align_values = ('top', 'middle', 'bottom', 'left', 'center', 'right')

def align(argument):
    return directives.choice(argument, align_values)

def image(name, arguments, options, content, lineno,
          content_offset, block_text, state, state_machine):
    reference = ''.join(arguments[0].split('\n'))
    if reference.find(' ') != -1:
        error = state_machine.reporter.error(
              'Image URI contains whitespace.',
              nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    options['uri'] = reference
    image_node = nodes.image(block_text, **options)
    return [image_node]

image.arguments = (1, 0, 1)
image.options = {'alt': directives.unchanged,
                 'height': directives.nonnegative_int,
                 'width': directives.nonnegative_int,
                 'scale': directives.nonnegative_int,
                 'align': align,
                 'class': directives.class_option}

def figure(name, arguments, options, content, lineno,
           content_offset, block_text, state, state_machine):
    figwidth = options.setdefault('figwidth')
    figclass = options.setdefault('figclass')
    del options['figwidth']
    del options['figclass']
    (image_node,) = image(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)
    if isinstance(image_node, nodes.system_message):
        return [image_node]
    figure_node = nodes.figure('', image_node)
    if figwidth == 'image':
        if Image:
            # PIL doesn't like Unicode paths:
            try:
                i = Image.open(str(image_node['uri']))
            except (IOError, UnicodeError):
                pass
            else:
                figure_node['width'] = i.size[0]
    elif figwidth is not None:
        figure_node['width'] = figwidth
    if figclass:
        figure_node.set_class(figclass)
    if content:
        node = nodes.Element()          # anonymous container for parsing
        state.nested_parse(content, content_offset, node)
        first_node = node[0]
        if isinstance(first_node, nodes.paragraph):
            caption = nodes.caption(first_node.rawsource, '',
                                    *first_node.children)
            figure_node += caption
        elif not (isinstance(first_node, nodes.comment)
                  and len(first_node) == 0):
            error = state_machine.reporter.error(
                  'Figure caption must be a paragraph or empty comment.',
                  nodes.literal_block(block_text, block_text), line=lineno)
            return [figure_node, error]
        if len(node) > 1:
            figure_node += nodes.legend('', *node[1:])
    return [figure_node]

def figwidth_value(argument):
    if argument.lower() == 'image':
        return 'image'
    else:
        return directives.nonnegative_int(argument)

figure.arguments = (1, 0, 1)
figure.options = {'figwidth': figwidth_value,
                  'figclass': directives.class_option}
figure.options.update(image.options)
figure.content = 1
