from z3c.form.interfaces import IWidget
from z3c.relationfield.interfaces import IRelationChoice
from zope.schema import Choice, TextLine
from zope.schema._bootstrapinterfaces import ValidationError
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


UPLOAD_BEHAVIOURS = {
    'create': 'Create',
    'replace': 'Replace',
    'checkout': 'Checkout',
}


def _createUploadBehaviourVocab():
    """ Create zope.schema vocabulary for upload behaviours."""
    for beh_id, beh_name in UPLOAD_BEHAVIOURS.items():
        term = SimpleTerm(value=beh_id, token=str(beh_id), title=beh_name)
        yield term

upload_behaviour_vocab = SimpleVocabulary(list(_createUploadBehaviourVocab()))


class IReferenceUploadField(IRelationChoice):
    """ Reference upload field marker for z3c.form """

    destination = TextLine(
        title=u'Destination',
        description=u'The path to the destination folder.',
        required=True,
        default=u'',
    )

    upload_behaviour = Choice(
        title=u'Upload behaviour',
        description=u'The name of the content type to be created.',
        vocabulary=upload_behaviour_vocab,
        default="create",
    )


class IReferenceUploadWidget(IWidget):
    """ Reference upload widget marker for z3c.form """


class ObjectDoesntExist(ValidationError):
    __doc__ = u"Referenced object doesn't exist"


class WrongUploadFileType(ValidationError):
    __doc__ = u"Can't replace image with file"
