import importlib

from django.db import models


class Activity(models.Model):
    source_class = models.CharField(max_length=100)
    source_id = models.PositiveIntegerField()
    title = models.CharField(max_length=150)
    published_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('source_class', 'source_id'),)

    def __unicode__(self):
        return u'%s:%s => %s' % (self.source_class, self.source_id, self.title)

    @property
    def source_instance(self):
        module_name = '.'.join(self.source_class.split('.')[:-1])
        class_name = self.source_class.split('.')[-1]
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            obj = cls.objects.get(pk=self.source_id)
            return obj
        except ImportError:
            return None
        except cls.DoesNotExist:
            return None


def broadcast(source, title):
    return Activity.objects.create(
        source_class=u'.'.join((source.__module__, source.__class__.__name__)),
        source_id=source.pk,
        title=title
    )
