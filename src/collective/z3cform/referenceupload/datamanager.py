import mimetypes

import zope.publisher.browser
import ZPublisher.HTTPRequest

from zope.component import adapts, getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from z3c.objpath.interfaces import IObjectPath
from z3c.relationfield.interfaces import IRelationValue
from plone.app.relationfield.widget import RelationDataManager

from .interfaces import IReferenceUploadField

FILE_UPLOAD = (
    zope.publisher.browser.FileUpload,
    ZPublisher.HTTPRequest.FileUpload,
)


class ReferenceUploadDataManager(RelationDataManager):
    """Reference upload data manager"""

    adapts(Interface, IReferenceUploadField)

    def set(self, value):
        """Sets the relationship target, creates a new instance of
        image/file object if upload is done
        """
        # No value to store
        if value is None:
            return super(ReferenceUploadDataManager, self).set(None)

        # Obtain current value
        current = None
        try:
            current = super(ReferenceUploadDataManager, self).get()
        except AttributeError:
            pass

        # Create object from uploaded file
        if isinstance(value, FILE_UPLOAD):
            value = self.create_object(value)

        object_path = getUtility(IObjectPath)
        obj = object_path.resolve(value)
        intids = getUtility(IIntIds)
        to_id = intids.register(obj)

        if IRelationValue.providedBy(current):
            # If we already have a relation, just set the to_id
            current.to_id = to_id
        else:
            # otherwise create a relationship
            super(ReferenceUploadDataManager, self).set(obj)

    def create_object(self, fileobj):
        """Creates object of appropriate type (Image/File) and returns
        it's physical path.
        """
        filename = fileobj.filename
        site = getSite()
        dest_path = self.field.destination.strip('/')
        folder = site.restrictedTraverse(str(dest_path))
        content = 'File'
        mimetype = mimetypes.guess_type(filename)[0] or ""
        if mimetype.startswith('image'):
            content = 'Image'

        # Create the new content
        old_id = folder.generateUniqueId(content)
        new_id = folder.invokeFactory(content, id=old_id, title=filename)
        obj = getattr(folder, new_id)
        obj._renameAfterCreation()
        obj.unmarkCreationFlag()
        obj.update_data(fileobj, mimetype)
        obj.reindexObject()
        return '/'.join(obj.getPhysicalPath())
