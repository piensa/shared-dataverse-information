"""
Models Used for the WorldMap Datatables API.  geonode.contrib.datatables

Regular Datatables API
And communication between GeoConnect and Worldmap
"""
from .models import TableJoinRequest, TableJoinResult, TABLE_JOIN_TO_RESULT_MAP
from django import forms


class TableJoinRequestForm(forms.ModelForm):
    """
    Used for the Worldmap table_join* API
        * geonode.contrib.datatables.views.table_join
    """
    class Meta:
        model = TableJoinRequest



class TableJoinResultForm(forms.ModelForm):
    """
    Used to validate incoming from WorldMap
    """
    class Meta:
        model = TableJoinResult
        widgets = {  'dataverse_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
                    , 'dataset_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
               # , 'name': forms.TextInput(attrs={'size':20})
                }


    @staticmethod
    def get_cleaned_data_from_table_join(table_join):
        """
        Given a WorldMap TableJoin* object:
            - Evaluate it against the TableJoinResultForm
            - Return the form's cleaned_data

        Method used to return WorldMap join results--expected to evaluate cleanly
            e.g. It works or throws an assertion error
        """
        f = TableJoinResultForm.create_form_from_table_join(table_join)

        assert f.is_valid(), "Data for TableJoinResultForm is not valid.  \nErrors:%s" % f.errors()

        return f.cleaned_data

    @staticmethod
    def create_form_from_table_join(table_join):
        """
        Format parameters using a WorldMap TableJoin* object
        (* geonode.contrib.datatables.TableJoin)
        """
        assert table_join is not None, "table_join cannot be None.  (It should be a WorldmMap geonode.contrib.datatables.TableJoin object"

        # ----------------------------------------------------------------------
        # Iterate through the dict linking TableJoin attributes
        #   to TableJoinResult fields
        #
        # ----------------------------------------------------------------------
        params = {}
        for new_key, attr_name in TABLE_JOIN_TO_RESULT_MAP.items():
            #print 'new_key/attr_name', new_key, attr_name

            # ----------------------------------------------------------------------
            # Make sure the table_join object has all the appropriate attributes
            #
            #   e.g. This should blow up if the TableJoin object changes in the future
            #       and doesn't have the required attrs
            # ----------------------------------------------------------------------
            attr_parts = attr_name.split('.')
            for idx in range(0, len(attr_parts)):
                obj_name = '.'.join(['table_join',] + attr_parts[0:idx] )
                #print 'check: %s - %s' % (obj_name, attr_parts[idx])
                assert hasattr(eval(obj_name), attr_parts[idx])\
                        , '%s object does not have a "%s" attribute.' % (obj_name, attr_parts[idx])

            # ----------------------------------------------------------------------
            # Add the attribute to the params dict
            # ----------------------------------------------------------------------
            param_val = eval('table_join.%s' % (attr_name))
            if hasattr(param_val, '__call__'):
                # We want the result of the function, e.g. join_layer.get_absolute_url
                params[new_key] = param_val.__call__()
            else:
                params[new_key] = param_val

        return TableJoinResultForm(params)

"""
python manage.py shell --settings=geonode.settings
from shared_dataverse_information.worldmap_datatables.forms import TableJoinResultForm
from geonode.contrib.datatables.models import *
tj = TableJoin.objects.all()[0]
f = TableJoinResultForm.create_form_from_table_join(tj)
f.is_valid()
f.cleaned_data
f2 = TableJoinResultForm(f.cleaned_data)
print f2.is_valid()
"""
