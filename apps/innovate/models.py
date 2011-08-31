from django.db import models

import caching.base


class BaseModelManager(caching.base.CachingManager):
    pass


class BaseModel(caching.base.CachingMixin, models.Model):
    objects = BaseModelManager()

    class Meta:
        abstract = True
