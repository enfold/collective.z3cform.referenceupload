from z3c.form.interfaces import IWidget
from z3c.relationfield.interfaces import IRelationChoice
from zope.schema._bootstrapinterfaces import ValidationError


class IReferenceUploadField(IRelationChoice):
    """ Reference upload field marker for z3c.form """


class IReferenceUploadWidget(IWidget):
    """ Reference upload widget marker for z3c.form """


class ObjectDoesntExist(ValidationError):
    __doc__ = u"Referenced object doesn't exist"
