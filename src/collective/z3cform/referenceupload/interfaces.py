from z3c.form.interfaces import IWidget
from z3c.relationfield.interfaces import IRelationChoice


class IReferenceUploadField(IRelationChoice):
    """ Reference upload field marker for z3c.form """


class IReferenceUploadWidget(IWidget):
    """ Reference upload widget marker for z3c.form """
