
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IForm
from z3c.form.widget import FieldWidget
from zope.interface import implements, implementer
from zope.component import getMultiAdapter, getUtility
from zope.component.hooks import getSite
from zope.pagetemplate.interfaces import IPageTemplate

from plone.app.iterate.dexterity.utils import get_working_copy
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import get_relateditems_options
from plone.app.widgets.utils import get_widget_form
from plone.app.z3cform.utils import call_callables
from plone.app.z3cform.widget import RelatedItemsWidget
from plone.formwidget.contenttree.widget import ContentTreeWidget
from plone.uuid.interfaces import IUUID

from .interfaces import IReferenceUploadWidget


class ReferenceUploadWidget(RelatedItemsWidget, ContentTreeWidget):
    """Reference upload widget"""

    implements(IReferenceUploadWidget)

    klass = u'reference-upload-widget'

    multi_select = False

    def raw_value(self):
        """Returns physical path of referenced object or None"""
        if self.request.get(self.name):
            return self.request.get(self.name)
        dm = getMultiAdapter((self.context, self.field), IDataManager)
        try:
            rel_obj = dm.get()
            if rel_obj:
                return IUUID(rel_obj)
        except:
            return None

    def object_value(self):
        """Returns the related object"""
        rel_uid = self.raw_value()
        if rel_uid:
            catalog = self.context.portal_catalog
            brains = catalog(UID=rel_uid)
            if brains:
                brain = brains[0]
                obj = brain.getObject()
                return obj

    def object_value_working_copy(self, obj):
        """Returns the related object's working copy if it exists"""
        wc = None
        if obj:
            wc = get_working_copy(obj)
        return wc

    def extract(self, default=NO_VALUE):
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
            IPageTemplate, name=DISPLAY_MODE)
        filename = ""
        obj = self.object_value()
        if wcopy:
            obj = self.object_value_working_copy(obj)
        if obj:
            if obj.portal_type == 'Image':
                if obj.image:
                    filename = obj.image.filename
            elif obj.portal_type == 'File':
                if obj.file:
                    filename = obj.file.filename
        return template(self, obj=obj, filename=filename)

    def render_input(self):
        args = super(RelatedItemsWidget, self)._base_args()
        args['name'] = self.name
        args['value'] = self.raw_value()
        args.setdefault('pattern_options', {})
        args['pattern_options']['maximumSelectionSize'] = 1
        field = self.field

        vocabulary_name = self.vocabulary

        field_name = self.field and self.field.__name__ or None

        context = self.context

        view_context = get_widget_form(self)
        # For EditForms and non-Forms (in tests), the vocabulary is looked
        # up on the context, otherwise on the view
        if (
            IEditForm.providedBy(view_context) or
            not IForm.providedBy(view_context)
        ):
            view_context = context

        root_search_mode = (
            args['pattern_options'].get('mode', None) and
            'basePath' not in args['pattern_options']
        )

        args['pattern_options'] = dict_merge(
            get_relateditems_options(
                view_context,
                args['value'],
                self.separator,
                vocabulary_name,
                self.vocabulary_view,
                field_name,
            ),
            args['pattern_options']
        )

        if root_search_mode:

            # Delete default basePath option in search mode, when no basePath
            # was explicitly set.
            del args['pattern_options']['basePath']
        if (
            not self.vocabulary_override and
            field and
            getattr(field, 'vocabulary', None)
        ):
            # widget vocab takes precedence over field
            form_url = self.request.getURL()
            source_url = '{0:s}/++widget++{1:s}/@@getSource'.format(
                form_url,
                self.name
            )
            args['pattern_options']['vocabularyUrl'] = source_url

        dest_folder = getattr(self.field, 'destination', None)
        if dest_folder:
            root_path = '/'.join(self.context.portal_url.getPortalObject().getPhysicalPath())
            args['pattern_options']['rootPath'] = root_path + dest_folder
            args['pattern_options']['basePath'] = root_path + dest_folder
            args['pattern_options']['mode'] = 'browse'

        pattern_widget = self._base(**args)
        if getattr(self, 'klass', False):
            pattern_widget.klass = u'{0} {1}'.format(
                pattern_widget.klass, self.klass
            )

        related_items_widget = pattern_widget.render()

        template = getMultiAdapter(
            (self.context, self.request, self.form, self.field, self),
            IPageTemplate, name=INPUT_MODE)
        return template(self, related_items_widget=related_items_widget)

    def render(self):
        if self.mode == 'display':
            results = self.render_display()
        elif self.mode == 'input':
            results = self.render_input()
        return results


@implementer(IFieldWidget)
def ReferenceUploadFieldWidget(field, request):
    """IFieldWidget factory for ReferenceUploadWidget."""
    return FieldWidget(field, ReferenceUploadWidget(request))
