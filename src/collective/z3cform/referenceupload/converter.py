from zope.component import adapts
from z3c.form.converter import FileUploadDataConverter

from .interfaces import IReferenceUploadField, IReferenceUploadWidget


class ReferenceUploadDataConverter(FileUploadDataConverter):
    """Data converter for Reference Upload field/widget"""

    adapts(IReferenceUploadField, IReferenceUploadWidget)

    def toFieldValue(self, value):
        """See z3c.form.interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        return self.field.fromUnicode(value)
