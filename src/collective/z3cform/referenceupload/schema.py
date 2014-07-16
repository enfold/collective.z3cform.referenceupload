from zope.interface import implements
from zope.schema.interfaces import IFromUnicode
from z3c.relationfield.schema import RelationChoice

from .datamanager import FILE_UPLOAD
from .interfaces import IReferenceUploadField, ObjectDoesntExist


class ReferenceUploadField(RelationChoice):
    """Reference Upload Field"""

    implements(IReferenceUploadField, IFromUnicode)

    def _validate(self, value):
        if isinstance(value, FILE_UPLOAD):
            return
        try:
            obj = self.context.restrictedTraverse(value)
            return super(ReferenceUploadField, self)._validate(obj)
        except KeyError:
            raise ObjectDoesntExist(value)

    def fromUnicode(self, value):
        if isinstance(value, unicode):
            return value.encode()
        return value
