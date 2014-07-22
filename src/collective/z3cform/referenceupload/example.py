from zope import schema
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.directives import form

from .schema import ReferenceUploadField
from .widget import ReferenceUploadFieldWidget


class IExample(form.Schema):
    """Schema for example content item with reference upload field"""

    form.widget('upload', ReferenceUploadFieldWidget)

    title = schema.TextLine(
        title=u"Title",
        description=u"Content title",
    )

    upload = ReferenceUploadField(
        title=u"Reference upload field",
        required=False,
        source=ObjPathSourceBinder(),
        destination='/destination_folder'
    )
