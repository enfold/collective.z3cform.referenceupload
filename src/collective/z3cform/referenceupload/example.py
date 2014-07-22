from zope import schema
from five import grok
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.directives import form
from plone.directives import dexterity

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


class Add(dexterity.AddForm):
    """An overloaded add form for our Example dx content type"""
    grok.name('collective.z3cform.referenceupload.example')

    def updateWidgets(self):
        """Override the destination folder based on request params"""
        super(Add, self).updateWidgets()

        # let's get the destination folder based on context path
        # (by adding '${typename}/upload' suffix, remember to create such
        # contained earlier)
        path = '/'.join(self.context.getPhysicalPath())
        new_destination = '/'.join((path, self.portal_type, 'upload'))
        self.widgets['upload'].field.destination = new_destination

        # let's set the initial location where the content browser popup will
        # be opened
        ntq = self.widgets['upload'].source.navigation_tree_query.copy()
        ntq['path']['query'] = new_destination
        self.widgets['upload'].field.source.navigation_tree_query = ntq


class Edit(dexterity.EditForm):
    """An overloaded edit form for our Example dx content type"""
    grok.context(IExample)

    def updateWidgets(self):
        """Override the destination folder based on request params"""
        super(Edit, self).updateWidgets()

        # let's get the destination folder based on context path
        # (by adding '${typename}/upload' suffix, remember to create such
        # contained earlier)
        path = '/'.join(self.context.aq_parent.getPhysicalPath())
        new_destination = '/'.join((path, self.portal_type, 'upload'))
        self.widgets['upload'].field.destination = new_destination

        # let's set the initial location where the content browser popup will
        # be opened
        ntq = self.widgets['upload'].source.navigation_tree_query.copy()
        ntq['path']['query'] = new_destination
        self.widgets['upload'].field.source.navigation_tree_query = ntq
