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
from plone.app.iterate.dexterity.utils import get_working_copy
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.relation import WorkingCopyRelation
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import modified

from .interfaces import IReferenceUploadField

from plone import api


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

        site = getSite()
        catalog = site.portal_catalog
        brains = catalog(UID=value)
        if brains:
            brain = brains[0]
            obj = brain.getObject()

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
                fileobj, filename, dest_folder, content_type)
        elif upload_behaviour == 'replace':
            return self.replace_object(fileobj, related, filename, content_type)
        else:
            return self.checkout_object(fileobj, related, filename, content_type)

    def create_object(self, fileobj, filename, dest_folder, content_type):
        """Creates object of appropriate type (Image/File) and returns
        it's physical path.
        """
        obj = api.content.create(
            container=dest_folder,
            type=content_type,
            title=filename,
            safe_id=True,
        )
        if content_type == "File":
            obj.file = NamedBlobFile(
                data=fileobj.read(),
                filename=filename.decode('utf-8')
            )
        elif content_type == "Image":
            obj.image = NamedBlobImage(
                data=fileobj.read(),
                filename=filename.decode('utf-8')
            )
        modified(obj)
        return IUUID(obj)

    def replace_object(self, fileobj, related, filename, content_type):
        """Replaces the content of uploaded file/image at related object
        """

        if content_type == "File":
            related.file = NamedBlobFile(
                data=fileobj.read(),
                filename=filename.decode('utf-8')
            )
        elif content_type == "Image":
            related.image = NamedBlobImage(
                data=fileobj.read(),
                filename=filename.decode('utf-8')
            )
        modified(related)
        return IUUID(related)

    def checkout_object(self, fileobj, related, filename, content_type):
        """Replaces the content of uploaded file/image at the working copy
        of the related object
        """
        control = getMultiAdapter(
            (related, self.context.REQUEST), name=u"iterate_control")
        policy = ICheckinCheckoutPolicy(related)
        working_copy = get_working_copy(related)
        if not working_copy:
            if control.checkout_allowed():
                folder = related.aq_parent
                working_copy = policy.checkout(folder)
            else:
                raise Exception(u"Can't obtain working copy.")

        if content_type == "File":
            working_copy.file = NamedBlobFile(
                data=fileobj.read(),
                filename=filename.decode('utf-8')
            )
        elif content_type == "Image":
            working_copy.image = NamedBlobImage(
                data=fileobj.read(),
                filename=filename.decode('utf-8')
            )
        modified(working_copy)
        return IUUID(related)
