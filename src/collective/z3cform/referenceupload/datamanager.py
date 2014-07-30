import mimetypes

import zope.publisher.browser
import ZPublisher.HTTPRequest

from zope.component import adapts, getUtility, getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from z3c.objpath.interfaces import IObjectPath
from z3c.relationfield.interfaces import IRelationValue
from plone.app.relationfield.widget import RelationDataManager
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.relation import WorkingCopyRelation

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

        # Create/update object with uploaded file (based on chosen behaviour)
        if isinstance(value, FILE_UPLOAD):
            value = self.manage_upload(value)

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

    def manage_upload(self, fileobj):
        """Dispatch action of managing the uploaded file based on chosen
        upload behaviour.
        """
        filename = fileobj.filename
        site = getSite()
        dest_path = self.field.destination.strip('/')
        dest_folder = site.restrictedTraverse(str(dest_path))
        upload_behaviour = self.field.upload_behaviour
        related = self.get()

        # determine content type of uploaded object
        content_type = 'File'
        mimetype = mimetypes.guess_type(filename)[0] or ""
        if mimetype.startswith('image'):
            content_type = 'Image'

        if not related or upload_behaviour == 'create':
            return self.create_object(
                fileobj, filename, dest_folder, content_type, mimetype)
        elif upload_behaviour == 'replace':
            return self.replace_object(fileobj, related, mimetype)
        else:
            return self.checkout_object(fileobj, related, mimetype)

    def create_object(self, fileobj, filename, dest_folder, content_type,
                      mimetype):
        """Creates object of appropriate type (Image/File) and returns
        it's physical path.
        """
        old_id = dest_folder.generateUniqueId(content_type)
        new_id = dest_folder.invokeFactory(
            content_type, id=old_id, title=filename)
        obj = getattr(dest_folder, new_id)
        obj._renameAfterCreation()
        obj.unmarkCreationFlag()
        obj.update_data(fileobj, mimetype)
        obj.reindexObject()
        return '/'.join(obj.getPhysicalPath())

    def replace_object(self, fileobj, related, mimetype):
        """Replaces the content of uploaded file/image at related object
        """
        related.update_data(fileobj, mimetype)
        related.reindexObject()
        return '/'.join(related.getPhysicalPath())

    def checkout_object(self, fileobj, related, mimetype):
        """Replaces the content of uploaded file/image at the working copy
        of the related object
        """
        control = getMultiAdapter(
            (related, self.context.REQUEST), name=u"iterate_control")
        policy = ICheckinCheckoutPolicy(related)
        working_copies = related.getBRefs(WorkingCopyRelation.relationship)
        if control.checkout_allowed():
            folder = related.aq_parent
            working_copy = policy.checkout(folder)
        elif working_copies:
            working_copy = working_copies[0]
        else:
            raise Exception(u"Can't obtain working copy.")

        working_copy.update_data(fileobj, mimetype)
        working_copy.reindexObject()
        return '/'.join(related.getPhysicalPath())
