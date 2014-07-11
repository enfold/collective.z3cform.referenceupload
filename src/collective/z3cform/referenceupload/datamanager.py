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
        if value is None:
            return super(ReferenceUploadDataManager, self).set(None)
        current = None
        try:
            current = super(ReferenceUploadDataManager, self).get()
        except AttributeError:
            pass

        if isinstance(value, FILE_UPLOAD):
            filename = value.filename
            filecontent = value.read()
            container = getSite()
            kwargs = {
                'image': filecontent
            }
            new_image_id = container.invokeFactory('Image', filename, **kwargs)
            obj = getattr(container, new_image_id)
            value = '/'.join(obj.getPhysicalPath())

        object_path = getUtility(IObjectPath)
        obj = object_path.resolve(value)

        intids = getUtility(IIntIds)
        to_id = intids.getId(obj)

        if IRelationValue.providedBy(current):
            # If we already have a relation, just set the to_id
            current.to_id = to_id
        else:
            # otherwise create a relationship
            super(ReferenceUploadDataManager, self).set(obj)
