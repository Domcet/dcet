class ApartmentDataExecutor:
    def __init__(self, item: dict = None):
        self.data = item.get('item', item)

    def execute_data(self):
        apartment_id = str(self.data.get('id')) if self.data.get('id') is not None else None
        apartment_balance = float(self.data.get('ufCrm9_1684774043')) if self.data.get('ufCrm9_1684774043') is not None else None

        apartment_fields = {
            'apartment_id': apartment_id,
            'title': str(self.data.get('title')) if self.data.get('title') is not None else None,
            'apartment_balance': float(apartment_balance) if apartment_balance is not None else 0,
            'tariff': str(self.data.get('ufCrm9_1684821535720')) if self.data.get('ufCrm9_1684821535720') is not None else None,
            'accrual': str(self.data.get('ufCrm9_1695918640745')) if self.data.get('ufCrm9_1695918640745') is not None else None,
            'privilege': str(self.data.get('ufCrm9_1696004188251')) if self.data.get('ufCrm9_1696004188251') is not None else None,
            'was_accrual_performed': str(self.data.get('ufCrm9_1709186235')) if self.data.get('ufCrm9_1709186235') is not None else None,
            'microdistrict': str(self.data.get('ufCrm9_1679074861')) if self.data.get('ufCrm9_1679074861') is not None else None,
            'house': str(self.data.get('ufCrm9_1679074876')) if self.data.get('ufCrm9_1679074876') is not None else None,
            'apartment': str(self.data.get('ufCrm9_1679074899')) if self.data.get('ufCrm9_1679074899') is not None else None,
            'personal_account': str(self.data.get('ufCrm9_1679074951')) if self.data.get('ufCrm9_1679074951') is not None else None,
            'contact': str(self.data.get('contactId')) if self.data.get('contactId') is not None else None,
        }

        return apartment_id, apartment_fields

