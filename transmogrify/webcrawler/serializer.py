from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
import logging
import os
import sys
from pickle import dump, load, PicklingError


"""
transmogrify.webcrawler.serializer
==================================

A blueprint that saves/restores stuff in pipeline

Options:

:directory

  Directory to store cached content in

:action

  Save or Restore

"""


class SerializerSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        self.action = options.get('action')
        if self.action not in ['save', 'restore']:
            raise AttributeError, "action has to be save or restore"
        self.directory = options.get('directory')
        self.logger = logging.getLogger(name)
        if not os.access(self.directory, os.F_OK):
            os.makedirs(self.directory)

    def __iter__(self):
        if self.action == 'save':
            return self.save()
        else:
            return self.restore()

    def restore(self):
        fp = open('%s/max' % self.directory)
        n_item = load(fp)
        fp.close()
        for x in xrange(n_item):
            fp = open('%s/%s' % (self.directory, x))
            item = load(fp)
            fp.close()
            item_type = item.get('_type', None)
            self.logger.debug("Serializer returning: %d %s" % (x, item))
            if item_type == 'Image':
                fp = open('%s/image.%s' % (self.directory, item['image']))
                item['image'] = fp.read()
                fp.close()
            elif item_type == 'File':
                fp = open('%s/file.%s' % (self.directory, item['file']))
                item['file'] = fp.read()
                fp.close()
            yield item

    def save(self):
        n_item = 0
        n_image = 0
        for item in self.previous:
            fp = open('%s/%s' % (self.directory, n_item), 'w')
            item_type = item.get('_type', None)
            if item_type == 'Image':
                fp1 = open('%s/image.%s' % (self.directory, n_image), 'w')
                fp1.write(item['image'].read())
                fp1.close()
                item['image'] = n_image
                n_image += 1
            elif item_type == 'File':
                fp1 = open('%s/file.%s' % (self.directory, n_image), 'w')
                fp1.write(item['file'].read())
                fp1.close()
                item['file'] = n_image
                item['_content_info'] = ''
                n_image += 1
            try:
                dump(item, fp)
            except PicklingError:
                self.logger.error("Serializer pickling: %s" % (item,))
            fp.close()
            n_item += 1
            self.logger.debug("Serializer saving: %d %s" % (n_item, item))
        fp = open('%s/max' % self.directory, 'w')
        dump(n_item, fp)
        fp.close()
        yield None
