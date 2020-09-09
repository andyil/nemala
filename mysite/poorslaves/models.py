from django.db import models

# Create your models here.


from django.db import models
from django.utils.translation import gettext as _, pgettext




class Document(models.Model):

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")


    url = models.CharField(_("url"), max_length=500)
    views = models.IntegerField(_("views"), default=0)
    answers = models.IntegerField(_("responded"), default=0)
    metadata = models.CharField(_("metadata"), max_length=500)
    last_shown = models.DateTimeField(null=True)
    contentType = models.CharField(max_length=500)


    def __str__(self):
        return pgettext("document model name", "xxy %(id)s") % {'id': self.id}

class Answer(models.Model):

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")


    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name=_("document"))
    choice_text = models.CharField(max_length=4096)

    user = models.CharField(max_length=20, null=True)
    created = models.DateTimeField(null=True)
    accepted = models.NullBooleanField(null=True)

