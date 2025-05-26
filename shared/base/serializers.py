from rest_framework import serializers


class DynamicFieldModelSerializer(serializers.ModelSerializer):
    
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        
        
        if fields:
            fields = set(fields.split(','))
            existing = set(self.fields)
            for field in existing - fields:
                self.fields.pop(field)