
from plone.dexterity.content import Item
from zope.interface import Interface
from zope.interface import implements


class IExample(Interface):
    """
    """


class Example(Item):
    implements(IExample)
