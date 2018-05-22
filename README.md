# django_filterjs

A django-backend for filter.js library https://github.com/jiren/filter.js

Module is under heavy development, many things may still change.

## Usage

### Import module to your view:

```python
from filterjs import filterjs
```

Create custom class:
```python
class MyFilter(filterjs.FilterJsSet):
    class Meta:
        model = MyModel

        fields = [ 'field1', 'field2', 'field3' ]
        override_filter_label = {
            'field1' : 'Field1 filter',
            'field2' : 'Field2 filter',
            'field3' : 'FIeld3 filter',
        }
        override_filter_value = {
            'field1' : { 'value1' : 'Value 1', 'value2' : 'Value 2' },
        }
```
`fields` allow do select fields to be used by filter. `override_filter_labels` allows to redefine text displayed by the filter for a given field, default is the field name with capitalized first letter. `override_filter_value` allows to override text displayed by the filter for a given value from the model. By default the value from the model is used. If the model field is e.g. BooleanField, the values will be 'True' and 'False', adn they can be overwritten to anything else more meaningful.

### Create a response:
```python
f = MyFilter(request.GET, queryset=MyModel.objects.all())
f_data = f.filter_data()
f_form = filterjs.DynamicFilterJsForm(request.POST, filter=f)

return render(request, 'template.html', {
    'criteria' : f.render_criteria(),
    'data' : f_data,
    'form': f_form
});
```
where `f_data` are the jsoned data and `f_form` is the filter form. At the moment all filter fields are rendered as a check boxes. IN future this will be configurable.

`Filter.js` requires to set render criteria, e.g.
```javascript
FJS.addCriteria({ field:'field1', ele : '#id_field1 input:checkbox', all:'all' });
```
This can be done manually in the template or using buildin function `render_criteria()` which requires following code in the template:
```python
{% autoescape off %}
{% for c in criteria %}
{{ c }}{% endfor %}
{% endautoescape %}
```

### Prepare template

The example template can be:
```javascript
$(document).ready(function(){
  var filterdata = {{ data }};

  var fd = filterdata[0];

  var afterFilter = function(result, jQ){
    $('#total_results').text(result.length);

  var FJS = FilterJS(results, '#results', {
    template: '#result-template',
    search: { ele: '#searchbox' },
    filter_on_init: true, // Default filter_on_init is false
    callbacks: {
      afterFilter: afterFilter
    },
  });

  {% autoescape off %}
  {% for c in criteria %}
  {{ c }}{% endfor %}
  {% endautoescape %}
  window.FJS = FJS;
});
```