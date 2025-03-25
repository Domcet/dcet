class KaspiResponse:
    def __init__(self, txn_id):
        self.txn_id = txn_id

    def make_response(self, result, address=None, debt=None, summ=None, prv_id=None):
        response_data = {
            'txn_id': self.txn_id,
            'result': result,
            'fields': {
                'field1': {'@name': 'address', '#text': address},
                'field2': {'@name': 'debt', '#text': debt if debt else 0},
            }
        }
        if summ is not None:
            response_data['summ'] = summ
        if prv_id is not None:
            response_data['prv_id'] = prv_id
        return response_data


    def make_error_response(self):
        return {
            "txn_id": self.txn_id,
            "result": 1
        }
