from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe


class ImageFileInput(ClearableFileInput):
    """
    Simplified clearable file input. Clear checkbox will be handled in the
    template as we have access to the model instance there.
    """
    template_with_initial = u'%(input)s'

    def render(self, name, value, attrs=None):
        return mark_safe(self.template_with_initial % {
            'input': super(ImageFileInput, self).render(name, value, attrs),
        })
