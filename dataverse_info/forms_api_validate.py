import hashlib

from django.core.exceptions import ValidationError
from django import forms

from django.conf import settings

from dataverse_info.models import DataverseInfo

SIGNATURE_KEY = 'SIGNATURE_KEY'

class APIValidateHelperForm(forms.ModelForm):
    """
    For API use.  Initial method.
    
    This function must be implemented for each concrete ModelForm:
        "def get_validate_field_names(self)"
             
    When a POST request is received, methods on this form are used for valiation.    

    e.g.  /dataverse/view-embedded-layer/
    
    PARAMS SENT TO API: { 'dv_user_id' : '--val--'
                        ,  'datafile_id' : '--val--'
                        , 'layer_name' : '--val--'
                        , 'SIGNATURE_KEY' : 'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2'
                  }
    Note: "SIGNATURE" param is handled outside of this form 
            and is sent separately to the "is_signature_valid(self, signature_value)" method
    
        
    """
    def get_validation_field_names(self):
        """
        Abstract.  Implement this for each form

        example:
        return ( 'dv_user_id',  'datafile_id')

        """
        raise AssertionError('This method must be implemented for each Form: %s' % type(self))


    def get_api_signature(self):
        if hasattr(self, 'cleaned_data') is False:
            raise AssertionError('Form is invalid.  cleaned_data is not available')
        
        val_list = []
        for key in self.get_validation_field_names():
            val = self.cleaned_data.get(key, None)
            if val is None:
                raise ValueError('Value for key "%s" cannot be None' % key)
            val_list.append('%s' % val)
            
        val_str = '|'.join(val_list + [settings.WORLDMAP_TOKEN_FOR_DATAVERSE])
        
        
        return hashlib.sha224(val_str).hexdigest()
        
        
    def is_signature_valid(self, signature_value):
        """
        After the form is found to be valid
        """
        assert signature_value is not None, "signature_value cannot be None"
        assert len(signature_value) > 50, "signature_value must be at least 50 chars in length"
        if hasattr(self, 'cleaned_data') is False:
            raise ValueError('Form is invalid.  cleaned_data is not available')

        if self.get_api_signature() == signature_value:
            return True
        return False
        
        
    def get_api_params_with_signature(self):
        if hasattr(self, 'cleaned_data') is False:
            raise AssertionError('Form is invalid.  cleaned_data is not available')
        
        params = self.cleaned_data
        params[SIGNATURE_KEY] = self.get_api_signature()
        return params
        
    
    class Meta:
        abstract = True
