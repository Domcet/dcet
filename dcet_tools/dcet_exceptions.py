class NotApartmentTypeId(Exception):
    def __init__(self):
        self.message = "Сущность с таким 'entity_type_id' не является квартирой"
        super().__init__(self.message)


class NoEntityTypeId(Exception):
    def __init__(self):
        self.message = "Не был предоставлен 'entity_type_id'"
        super().__init__(self.message)


class NotBusinessProcess(Exception):
    def __init__(self):
        self.message = "Запрос не явлется валидным бизнес-процессом битрикс"
        super().__init__(self.message)


class NotValidRequest(Exception):
    def __init__(self):
        self.message = "Запрос не явлется валидным"
        super().__init__(self.message)


class NotValidEvent(Exception):
    def __init__(self):
        self.message = "В запросе поле 'event' не является валидным"
        super().__init__(self.message)


class NoApartmentId(Exception):
    def __init__(self):
        self.message = "Отсутвует ID квартиры в запросе бизнес-процесса битрикс"
        super().__init__(self.message)


class NoApartmentItem(Exception):
    def __init__(self):
        self.message = "Не удалось получить квартиру из битрикс"
        super().__init__(self.message)


class NoApartmentDeleteId(Exception):
    def __init__(self):
        self.message = "Отсутвует ID удаляемой квартиры"
        super().__init__(self.message)


class NoPersonalAccount(Exception):
    def __init__(self):
        self.message = "Не был передан лицевой счет квартиры"
        super().__init__(self.message)


class NoTxnId(Exception):
    def __init__(self):
        self.message = "Не был передан 'txn_id'"
        super().__init__(self.message)


class BadKaspiPayRequestParams(Exception):
    def __init__(self):
        self.message = "Запрос Kaspi Pay передал невалидные параметры"
        super().__init__(self.message)


class ApartmentNotFound(Exception):
    def __init__(self):
        self.message = "Квартира не найдена в БД"
        super().__init__(self.message)


class ApartmentNotCreated(Exception):
    def __init__(self):
        self.message = "Квартира не создана"
        super().__init__(self.message)
