# -*- coding: utf-8 -*-
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout


class AddForm(DefaultAddForm):

    def updateWidgets(self):
        """Override the destination folder based on request params"""
        super(AddForm, self).updateWidgets()

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


class EditForm(DefaultEditForm):

    def updateWidgets(self):
        """Override the destination folder based on request params"""
        super(EditForm, self).updateWidgets()

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


EditView = layout.wrap_form(EditForm)


class AddView(DefaultAddView):
    """This is the default add view as looked up by the ++add++ traversal
    namespace adapter in CMF. It is an unnamed adapter on
    (context, request, fti).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = AddForm
