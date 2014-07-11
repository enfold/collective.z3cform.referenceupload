import z3c.form
from z3c.formwidget.query.widget import QuerySubForm, QueryContext
from zope.interface import implements, implementer
from zope.component import getMultiAdapter
from plone.formwidget.contenttree.widget import ContentTreeWidget

from .interfaces import IReferenceUploadWidget


class ReferenceUploadWidget(z3c.form.widget.Widget, ContentTreeWidget):
    """Reference upload widget"""

    implements(IReferenceUploadWidget)

    klass = u'reference-upload-widget'
    multi_select = False

    def formatted_value(self):
        dm = getMultiAdapter(
            (self.context, self.field), z3c.form.interfaces.IDataManager)
        try:
            rel = dm.get()
            if rel:
                return rel.tag()
        except TypeError:
            return None

    def update(self):
        self.subform = QuerySubForm(QueryContext(), self.request, self.name)
        self.subform.update()

    def renderQueryWidget(self):
        return ''

    def extract(self, default=z3c.form.interfaces.NO_VALUE):
        option = self.request.get(self.name + '_option')
        if option == u'upload':
            file_upload = self.request.get(self.name + '_file')
            if file_upload and file_upload[0]:
                file_upload = file_upload[0]
                if file_upload.filename:
                    return file_upload
        elif option == u'select':
            return self.request.get(self.name)
        return default


@implementer(z3c.form.interfaces.IFieldWidget)
def ReferenceUploadFieldWidget(field, request):
    """IFieldWidget factory for ReferenceUploadWidget."""
    return z3c.form.widget.FieldWidget(field, ReferenceUploadWidget(request))
