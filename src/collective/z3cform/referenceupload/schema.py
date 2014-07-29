import mimetypes

from zope.interface import implements
from zope.schema.interfaces import IFromUnicode
from z3c.relationfield.schema import RelationChoice

from .datamanager import FILE_UPLOAD
from .interfaces import IReferenceUploadField, ObjectDoesntExist, \
    WrongUploadFileType


class ReferenceUploadField(RelationChoice):
    """Reference Upload Field"""

    implements(IReferenceUploadField, IFromUnicode)

    def __init__(self, destination=None, upload_behaviour='create', **kw):
        self.destination = destination
        self.upload_behaviour = upload_behaviour
        super(ReferenceUploadField, self).__init__(**kw)

    def _validate(self, value):
        # validate uploaded file
        if isinstance(value, FILE_UPLOAD):
            try:
                current_relation = self.get(self.context)
            except AttributeError:
                current_relation = None
            if current_relation:
                related_obj = current_relation.to_object
                if self.upload_behaviour == 'replace':
                    mimetype = mimetypes.guess_type(value.filename)[0] or ""
                    if related_obj.portal_type == 'Image':
                        if not mimetype.startswith('image'):
                            raise WrongUploadFileType()
            return
        # validate relation possibility
        try:
            obj = self.context.restrictedTraverse(value)
            return super(ReferenceUploadField, self)._validate(obj)
        except KeyError:
            raise ObjectDoesntExist(value)

    def fromUnicode(self, value):
        if isinstance(value, unicode):
            return value.encode()
        return value
