import inspect
from copy import copy
from typing import Generator

from behaviors.behaviors import Slugged, Timestamped
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property

__all__ = [
    'models',
    'DefaultManager',
    'DefaultModel',
    'TimestampedModel',
    'SluggedModel',
]


class DefaultQuerySet(models.QuerySet):
    Q = None
    """Q is a extension to Django queryset. Defining Q like this:
        class Q:
            @staticmethod
            def delivered():
                return Q(status__extended='delivered')
        Adds the method `delivered` to the queryset (and manager built on it), and
        allows you to reuse the returned Q object, like this:
        class OrderQuerySet:
            class Q:
                @staticmethod
                def delivered():
                    return Q(status__extended='delivered')
            def delivered_yesterday(self):
                return self.filter(self.Q.delivered & Q(delivery_date='2032-12-01'))
    """

    @classmethod
    def as_manager(cls):
        """Copy-paste of stock django as_manager() to use our default manager
        See also: https://github.com/django/django/blob/master/django/db/models/query.py#L198
        """
        manager = DefaultManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True

    def __getattr__(self, name):
        if self.Q is not None and hasattr(self.Q, name):
            return lambda *args: self.filter(getattr(self.Q, name)())

        raise AttributeError()

    def with_last_update(self):
        """Annotate `last_update` field that displays the creation or modification date"""
        return self.annotate(last_update=Coalesce(F('modified'), F('created')))


class DefaultManager(models.Manager):
    relations_to_assign_after_creation = []

    def __getattr__(self, name):
        if hasattr(self._queryset_class, 'Q') and hasattr(self._queryset_class.Q, name):
            return getattr(self.get_queryset(), name)

        raise AttributeError(f'Nor {self.__class__}, nor {self._queryset_class.__name__} or {self._queryset_class.__name__}.Q does not have `{name}` defined.')

    def create(self, *args, **kwargs):
        """
        Creation with particular generic relation values as kwargs
        Example:
            class CafeManager(DefaultManager):
                relations_to_assign_after_creation = ['dish']
            class Spam(models.Model):
                ...
            class Eggs(models.Model):
                ...
            class Cafe(models.Model):
                objects = CafeManager()
                dish_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
                dish_id = PositiveIntegerField()
                dish = GenericForeignKey('dish_type', 'dish_id')
            # Now you can use
            spam = Spam(...)
            eggs = Eggs(...)
            SpamCafe = Cafe.objects.create(dish=spam)
            EggsCafe = Cafe.objects.create(dish=eggs)
        """
        _stored_relations = {rel: kwargs.pop(rel) for rel in self.relations_to_assign_after_creation if rel in kwargs.keys()}

        instance = super().create(*args, **kwargs)

        for rel, val in _stored_relations.items():
            if val is not None:
                try:
                    setattr(instance, rel, val)
                except AttributeError:
                    raise FieldError('Bad relation field during creation!')

        instance.save()
        return instance


class DefaultModel(models.Model):
    objects = DefaultManager()

    class Meta:
        abstract = True

    @classmethod
    def get_contenttype(cls) -> ContentType:
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def has_field(cls, field) -> bool:
        """
        Shortcut to check if model has particular field
        """
        try:
            cls._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False

    @classmethod
    def list_fields(cls, include_parents=True) -> Generator:
        """
        Shortcut to list all field names.
        Accepts parameter `include_parents=False` with which returnes only fields defined in current model.
        This behaviour is little different from django's — its _meta.get_fields(include_parents=False) returns
        fields taken from inherited models, and we do not
        """
        if include_parents:
            return (field.name for field in cls._meta.get_fields(include_parents=True) if not isinstance(field, GenericRelation))

        else:
            parent_fields = set()

            for parent in inspect.getmro(cls):
                if issubclass(parent, models.Model) and hasattr(parent, '_meta'):  # if it is a django model
                    if not issubclass(parent, cls):  # ignore the lowest model in tree
                        for field in parent._meta.get_fields(include_parents=False):
                            if not isinstance(field, GenericRelation):
                                parent_fields.update([field.name])

            return (field.name for field in cls._meta.get_fields(include_parents=False) if field.name not in parent_fields)

    def update_from_kwargs(self, **kwargs):
        """
        A shortcut method to update model instance from the kwargs.
        """
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def setattr_and_save(self, key, value):
        """Shortcut for testing -- set attribute of the model and save"""
        setattr(self, key, value)
        self.save()

    def copy(self, **kwargs):
        """Creates new object from current."""
        instance = copy(self)
        kwargs.update({
            'id': None,
            'pk': None,
        })
        instance.update_from_kwargs(**kwargs)
        return instance

    @classmethod
    def get_label(cls) -> str:
        """
        Get a unique within the app model label
        """
        return cls._meta.label_lower.split('.')[-1]

    def clear_cached_properties(self):
        """Clears all used cached properties of instance."""

        for property_name in self._get_cached_property_names():
            try:
                del self.__dict__[property_name]
            except KeyError:
                pass

    def _get_cached_property_names(self):
        return [
            func_name
            for func_name in dir(self.__class__)
            if type(getattr(self.__class__, func_name)) is cached_property
        ]


class TimestampedModel(DefaultModel, Timestamped):
    """
    Default app model that has `created` and `updated` attributes.
    Currently based on https://github.com/audiolion/django-behaviors
    """
    class Meta:
        abstract = True


class SluggedModel(TimestampedModel, Slugged):
    """
    Currently based on https://github.com/audiolion/django-behaviors
    """
    class Meta:
        abstract = True
