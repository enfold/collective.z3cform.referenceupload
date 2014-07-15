from zope import schema
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.directives import form

from .schema import ReferenceUploadField
from .widget import ReferenceUploadFieldWidget


class IExample(form.Schema):
    """Schema for example content item with reference upload field"""

    form.widget('upload', ReferenceUploadFieldWidget)
    form.widget('upload2', ReferenceUploadFieldWidget)

    title = schema.TextLine(
        title=u"Title",
        description=u"Content title",
    )

    upload = ReferenceUploadField(
        title=u"Reference upload field",
        required=True,
        source=ObjPathSourceBinder(),
    )

    desc = schema.TextLine(
        title=u"Desc",
        description=u"Content Desc",
    )

    upload2 = ReferenceUploadField(
        title=u"Reference upload field 2",
        required=False,
        source=ObjPathSourceBinder(),
    )
