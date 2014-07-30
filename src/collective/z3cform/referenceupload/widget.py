import z3c.form

from z3c.formwidget.query.widget import QuerySubForm, QueryContext
from z3c.objpath.interfaces import IObjectPath
from zope.interface import implements, implementer
from zope.component import getMultiAdapter, getUtility
from zope.pagetemplate.interfaces import IPageTemplate

from plone.formwidget.contenttree.widget import ContentTreeWidget
from plone.app.iterate.relation import WorkingCopyRelation

from .interfaces import IReferenceUploadWidget


class ReferenceUploadWidget(z3c.form.widget.Widget, ContentTreeWidget):
    """Reference upload widget"""

    implements(IReferenceUploadWidget)

    klass = u'reference-upload-widget'
    multi_select = False

    def raw_value(self):
        """Returns physical path of referenced object or None"""
        if self.request.get(self.name):
            return self.request.get(self.name)
        dm = getMultiAdapter(
            (self.context, self.field), z3c.form.interfaces.IDataManager)
        try:
            rel_obj = dm.get()
            if rel_obj:
                return '/'.join(rel_obj.getPhysicalPath())
        except TypeError:
            return None

    def object_value(self):
        """Returns the related object"""
        rel_path = self.raw_value()
        if rel_path:
            object_path = getUtility(IObjectPath)
            obj = object_path.resolve(str(rel_path))
            if obj:
                return obj

    def object_value_working_copy(self, obj):
        """Returns the related object's working copy if it exists"""
        if obj:
            wcopies = obj.getBRefs(WorkingCopyRelation.relationship)
            if wcopies:
                return wcopies[0]

    def update(self):
        """Update widget"""
        self.subform = QuerySubForm(QueryContext(), self.request, self.name)
        self.subform.update()

    def renderQueryWidget(self):
        """Overloaded from z3c.formidget.query.widget.QuerySourceRadioWidget"""
        return ''

    def extract(self, default=z3c.form.interfaces.NO_VALUE):
        """Extract the value of submitted element from the request"""
        option = self.request.get(self.name + '_option')
        if option == u'upload':
            file_upload = self.request.get(self.name + '_file')
            if file_upload:
                if isinstance(file_upload, list):
                    file_upload = file_upload[0]
                if file_upload.filename:
                    return file_upload
        elif option == u'select':
            return self.request.get(self.name)
        elif option == u'keep':
            return self.request.get(self.name + '_raw_value')
        return default

    def render_display(self, wcopy=False):
        """Render the plain widget without additional layout"""
        template = getMultiAdapter(
            (self.context, self.request, self.form, self.field, self),
            IPageTemplate, name=z3c.form.interfaces.DISPLAY_MODE)
        obj = self.object_value()
        if wcopy:
            obj = self.object_value_working_copy(obj)
        return template(self, obj=obj)


@implementer(z3c.form.interfaces.IFieldWidget)
def ReferenceUploadFieldWidget(field, request):
    """IFieldWidget factory for ReferenceUploadWidget."""
    return z3c.form.widget.FieldWidget(field, ReferenceUploadWidget(request))
