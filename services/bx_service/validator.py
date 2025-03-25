from dcet_tools.dcet_exceptions import NotBusinessProcess, NoEntityTypeId, NotApartmentTypeId
import re


class BitrixRequestValidator:
    @classmethod
    def validate_bitrix_apartment_value(cls, value_to_validate):
        match = re.search(r'DYNAMIC_185_(\d+)', value_to_validate)

        if match:
            extracted_number = match.group(1)
            return {'success': True, 'extracted_number': extracted_number}
        else:
            raise NotBusinessProcess

    @classmethod
    def validate_bitrix_data(cls, data):
        entity_type_id = data.get('data[FIELDS][ENTITY_TYPE_ID]', None)
        entity_id = data.get('data[FIELDS][ID]', None)
        event = data.get('event', None)

        if not entity_type_id:
            raise NoEntityTypeId
        
        if entity_type_id != "185":
            raise NotApartmentTypeId
        
        return {
            'event': event,
            'id': entity_id,
            'entity': 'apartment'
        }
