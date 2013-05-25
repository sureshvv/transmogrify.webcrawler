from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
import logging
import os
import sys
from pickle import dump, load


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
            self.logger.debug("Serializer returning: %d %s" % (x, item))
            yield item

    def save(self):
        n_item = 0
        for item in self.previous:
            fp = open('%s/%s' % (self.directory, n_item), 'w')
            dump(item, fp)
            fp.close()
            n_item += 1
            self.logger.debug("Serializer saving: %d %s" % (n_item, item))
        fp = open('%s/max' % self.directory, 'w')
        dump(n_item, fp)
        fp.close()
        yield None
