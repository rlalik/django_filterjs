from django.core import serializers
from django import forms
from django.forms.fields import MultipleChoiceField
from django.forms.models import model_to_dict
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
import json

import collections

def to_dict(instance, only = None, exclude = None):
    assert not ((only is not None) and (exclude is not None)), \
        """to_dict(): only and exclude are mutually exclusive,
        use only one of them."""

    opts = instance._meta
    data = {}

    for f in opts.concrete_fields + opts.many_to_many:
        if only is not None and f.name not in only:
            continue
        if exclude is not None and f.name in exclude:
            continue

        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                ll = []
                for i in f.value_from_object(instance):
                    ll.append(str(i))
                data[f.name] = sorted(ll)
        elif isinstance(f, OneToOneField):
            if instance.pk is None:
                data[f.name] = []
            else:
                id = f.value_from_object(instance)
                vv = instance._meta.get_field(f.name).related_model.objects.get(pk=id)
                data[f.name] = to_dict(vv, exclude=[ 'id' ])
        elif isinstance(f, ForeignKey):
            if instance.pk is None:
                data[f.name] = []
            else:
                id = f.value_from_object(instance)
                vv = instance._meta.get_field(f.name).related_model.objects.get(pk=id)
                data[f.name] = to_dict(vv, exclude=[ 'id' ])
        else:
            data[f.name] = f.value_from_object(instance)
    return data

class FilterJsSetOptions(object):
    def __init__(self, options=None):
        self.model = getattr(options, 'model', None)
        self.fields = getattr(options, 'fields', None)
        self.filter = getattr(options, 'filter', 'FJS')
        self.override_filter_label = getattr(options, 'override_filter_label', None)
        self.override_filter_value = getattr(options, 'override_filter_value', None)

class FilterJsSetMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        new_class._meta = FilterJsSetOptions(getattr(new_class, 'Meta', None))
        new_class.base_fields = new_class.get_fields()

        return new_class

class BaseFilterJsSet(object):
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if queryset is None:
            queryset = self._meta.model._default_manager.all()
        model = queryset.model
        self.queryset = queryset

    @classmethod
    def get_fields(cls):
        """
        Resolve the 'fields' argument that should be used for generating filters on the
        filterset. This is 'Meta.fields' sans the fields in 'Meta.exclude'.
        """
        model = cls._meta.model
        fields = cls._meta.fields
        return fields
        #assert not (fields is None), \
            #"Setting 'Meta.model' without 'Meta.fields' is disallowed. " \
            #"Add an explicit 'Meta.fields' or 0 to the %s class." % cls.__name__

    def filter_data(cls):
        data = []
        for i in cls.queryset:
            data.append(cls.to_dict(i))
        return data

    def render_criteria(cls):
        criteria = []
        for field in cls._meta.model._meta.get_fields():
            if field.name in cls._meta.fields:
                c = "{:s}.addCriteria({{ field:'{:s}', ele : '#id_{:s} input:checkbox', all:'all' }});".format(
                    cls._meta.filter, field.name, field.name)
                criteria.append(c)
        return criteria

    def count_values(cls):
        values = {}
        for field in cls._meta.fields:
                values[field] = {}

        for instance in cls.queryset:
            for f in instance._meta.concrete_fields + instance._meta.many_to_many:
                if f.name not in cls._meta.fields:
                    continue
                v = []
                if isinstance(f, ManyToManyField):
                    if instance.pk is not None:
                        #v = list(f.value_from_object(instance).values_list(f.name, flat=True))ll = []
                        ll = []
                        for i in f.value_from_object(instance):
                            ll.append(str(i))
                        v = sorted(ll)
                else:
                    v = [ str(f.value_from_object(instance)) ]
                for _v in v:
                    if _v in values[f.name]:
                        values[f.name][_v]['all'] += 1
                    else:
                        values[f.name][_v] = { 'all' : 1 }

        for k, v in values.items():
            values[k] = collections.OrderedDict(sorted(v.items()))

        return values

    def json(self):
        return json.dumps(self.filter_data(), indent=1)

    @classmethod
    def to_dict(cls, instance):
        return to_dict(instance)

class FilterJsSet(BaseFilterJsSet, metaclass=FilterJsSetMetaclass):
    pass

class FilterCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    option_template_name = 'filterjs/input_option.html'

class DynamicFilterJsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        filter = kwargs.pop('filter')
        super(DynamicFilterJsForm, self).__init__(*args, **kwargs)
        dynamic_fields = filter.count_values()
        for key in dynamic_fields:
            v = []
            for val in dynamic_fields[key]:

                # override value labels
                if key in filter._meta.override_filter_value and val in filter._meta.override_filter_value[key]:
                    lval = filter._meta.override_filter_value[key][val]
                else:
                    lval = val

                # override values
                if val == "True":
                    fval = "true"
                elif val is "False":
                    fval = "false"
                else:
                    fval = val

                v += [(fval, "{:s} ({:d})".format(lval, dynamic_fields[key][val]['all']))]

            self.fields[key] = forms.fields.MultipleChoiceField(widget=FilterCheckboxSelectMultiple, choices=v, required=False)
            if key in filter._meta.override_filter_label:
                self.fields[key].label = filter._meta.override_filter_label[key]
