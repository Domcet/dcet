from dcet_tools.http_requests import bx24_post_request
from services.accrual_service.config import *


class Apartment:
    def __init__(self, apartment_data: dict, deal_name: str):
        self.apartment_data = apartment_data
        self.deal_name = deal_name
        self._validate_apartment_data()

    def _validate_apartment_data(self):
        if not isinstance(self.apartment_data, dict):
            raise ValueError("Невалидные поля квартиры")

        required_fields = ['id', 'title', balance, rate, exemption]
        missing_fields = [field for field in required_fields if field not in self.apartment_data]

        if missing_fields:
            raise KeyError(f"Отсутствуют обязательные поля квартиры: {', '.join(missing_fields)}")
    
    async def _get_apartment_tariff_price(self, rate_name: str) -> float:
        params = {
            "filter": {
                "CATALOG_ID": 15,
                "SECTION_ID": 97
            },
            "select": ["ID", "PRICE", "NAME"]
        }

        response = await bx24_post_request("crm.product.list", params)
        results = response.get("result", [])

        if not results:
            raise LookupError("Не удалось получить список тарифов из Bitrix")

        for product in results:
            if product.get("NAME") == rate_name:
                price = product.get("PRICE")
                if price is not None:
                    return float(price)
                else:
                    raise ValueError(f"У тарифа '{rate_name}' не указана цена")

        raise LookupError(f"Тариф с названием '{rate_name}' не найден")

    async def _has_apartment_exemption(self, ap_exemption: int) -> bool:
        ap_exemption = int(ap_exemption)
        if ap_exemption == have_exception:
            return True
        elif ap_exemption == no_exemption:
            return False
        else:
            raise ValueError("Некорректное значение льготы")
    
    async def _get_apartment_tariff_name(self, ap_rate: str):
        return {
            econom: "Эконом",
            basic: "Базовый",
            premium: "Премиум"
        }.get(ap_rate, "")

    async def _add_new_deal(self, amount: float, title: str, item_id: int):
        data_for_deal = {
            "fields": {
                'CURRENCY_ID': 'KZT',
                'OPPORTUNITY': amount,
                'TITLE': title,
                'ASSIGNED_BY_ID': 4923,
                'PARENT_ID_185': item_id,
                'OPENED': 'Y',
                'CATEGORY_ID': 11,
                'STAGE_ID': 'C11:WON',
            }
        }
        return await bx24_post_request("crm.deal.add", data_for_deal)

    async def _check_new_deal(self, deal_id: int, deal_data: list):
        deals = await self._get_deals_by_id(deal_id)
        result = deals["result"]
        if result:
            for deal in result:
                if deal["TITLE"] == str(deal_data[0]):
                    if deal["PARENT_ID_185"] == str(deal_data[1]):
                        if float(deal["OPPORTUNITY"]) == float(deal_data[2]):
                            return True 

                await self._delete_deal_by_id(deal_id=deal_id)
        
        raise Exception(f"Сделка с id {deal_id} была создана некорректно и была удалена")

    async def _update_apartment_balance(self, new_balance: float, ap_id: int):
        data_for_company = {
            balance: new_balance
        }

        return await bx24_post_request("crm.item.update", {
            "entityTypeId": 185,
            "id": ap_id,
            "fields": data_for_company
        })
    
    async def _get_deal_by_title(self, title: str) -> dict:
        params = {
            "filter": {
                "TITLE": title,
                "PARENT_ID_185": self.apartment_data['id']
            },
            "select": ["ID", "TITLE"]
        }

        response = await bx24_post_request("crm.deal.list", params)
        deals = response.get("result", [])

        if not deals:
            return False

        return deals[0]    
    
    async def _get_deals_by_id(self, deal_id: int):
        params = {
            "select": ["TITLE", "PARENT_ID_185", "OPPORTUNITY", "ASSIGNED_BY_ID", "CATEGORY_ID"],
            "filter": {
                "ID": deal_id
            }
        }
        return await bx24_post_request("crm.deal.list", params)

    async def _get_apartment_balance(self, apartment_id: int) -> float:
        params = {
            "entityTypeId": 185,
            "id": apartment_id
        }

        response = await bx24_post_request("crm.item.get", params)
        result = response.get("result", {}).get("item", {})

        if not result:
            raise LookupError(f"Квартира с ID {apartment_id} не найдена")

        if balance not in result:
            raise KeyError(f"Поле баланса '{balance}' отсутствует в данных квартиры")

        return float(result[balance])
    
    async def _check_apartment_balance(self, current_balance: float, new_balance: float, apartment_id: int, deal_id: int):
        if current_balance != new_balance:
            try:
                await self._update_apartment_balance(
                    new_balance=new_balance,
                    ap_id=apartment_id
                )
                return True
            except Exception as ex:
                await self.delete_deal_by_id(deal_id=deal_id)
                raise Exception(f"При начислении баланс квартиры с id {apartment_id} не обновился. Сделка откатилась. Причина: {str(ex)}")
            
        return True
        
    async def _delete_deal_by_id(self, deal_id: int):
        params = {
            "id": deal_id
        }
        return await bx24_post_request("crm.deal.delete", params)

    async def _add_comment(self, apartment_id: int, deal_id, summ: float):
        params = {
            "fields": {
                'ENTITY_TYPE': "dynamic_185",
                'ENTITY_ID': apartment_id,
                'COMMENT': f"Создана сделка по ежемесячному начислению https://domcet.bitrix24.kz/crm/deal/details/{deal_id}/. Сумма сделки: {summ}"
            }
        }
        result = await bx24_post_request("crm.timeline.comment.add", params)
        return result
    
    async def _prepare_data(self):
        ap_rate = self.apartment_data[rate]
        ap_exemption = self.apartment_data[exemption]
        ap_balance = self.apartment_data[balance]

        normal_ap_rate = await self._get_apartment_tariff_name(ap_rate)
        price = await self._get_apartment_tariff_price(normal_ap_rate)
        is_exempt = await self._has_apartment_exemption(ap_exemption)

        discount = price / 2 if is_exempt else price
        new_balance = ap_balance - discount

        return {
            "deal_summ": discount,
            "new_balance": new_balance 
        }
    
    async def do_sync_accrual(self, logger):        
        data = await self._prepare_data()
        ap_id = self.apartment_data['id']
        deal_summ = data["deal_summ"]
        new_balance = data["new_balance"]
        logger.info(f"Началось начисление для квартиры: id=[{ap_id}], имя=[{self.apartment_data['title']}], баланс=[{self.apartment_data[balance]}]")
        deal = await self._add_new_deal(amount=deal_summ, title=self.deal_name, item_id=ap_id)
        deal_id = deal["result"]

        try:
            await self._check_new_deal(deal_id, [self.deal_name, ap_id, deal_summ])
            await self._update_apartment_balance(new_balance=new_balance, ap_id=ap_id)

            current_balance = await self._get_apartment_balance(apartment_id=ap_id)

            await self._check_apartment_balance(
                current_balance=current_balance,
                new_balance=new_balance,
                apartment_id=ap_id,
                deal_id=deal_id
            )

            await self._add_comment(
                apartment_id=ap_id,
                deal_id=deal_id,
                summ=deal_summ
            )
            logger.info(f"Начисление для квартиры [id: {ap_id}, имя: {self.apartment_data['title']}] завершено. Новый баланс: {new_balance}. Старый баланс: {self.apartment_data[balance]}")

            return new_balance
        
        except Exception as ex:
            await self._delete_deal_by_id(deal_id=deal_id)
            raise Exception(
                f"Ошибка при начислении квартиры ID {ap_id}. "
                f"Сделка была удалена. Причина: {str(ex)}"
            )
        