from dcet_tools.http_requests import bx24_post_request, bx24_get_request
from dcet_tools.exception_decorator import catch_exception


class KaspiHttpService:
    async def get_apartment_info(self, entity_element_id: int):
        result = await bx24_get_request(
            url="crm.item.get",
            params={
                "entityTypeId": 185,
                "id": entity_element_id
            }
        )
        return result 

    async def add_deal(self, payload: dict) -> dict:
        return await bx24_post_request(
            url="crm.deal.add",
            payload=payload
        )

    async def update_apartment(self, payload: dict) -> dict:
        return await bx24_post_request(
            url="crm.item.update",
            payload=payload
        )

    async def delete_deal(self, deal_id: int) -> dict:
        try:
            return await bx24_post_request(
                url="crm.deal.delete",
                payload={"id": deal_id}
            )
        except Exception as ex:
            raise Exception(f"Ошибка при удалении сделки {deal_id}") from ex

    async def add_comment(self, payload: dict) -> dict:
        return await bx24_post_request(
            url="crm.timeline.comment.add",
            payload=payload
        )

    @catch_exception("kaspi.log")
    async def kaspi_pay_update(self, summ, account, txn_id, balance, apartment_id, date_create):
        try:
            new_balance = float(summ) if balance is None else float(balance) + float(summ)

            data_for_deal = {
                "fields": {
                    'CURRENCY_ID': 'KZT',
                    'OPPORTUNITY': summ,
                    'TITLE': f"{account} Пополнение каспи {txn_id}",
                    'ASSIGNED_BY_ID': 4923,
                    'PARENT_ID_185': apartment_id,
                    'OPENED': 'Y',
                    'CATEGORY_ID': 25,
                    'STAGE_ID': 'C25:WON',
                    'UF_CRM_1732177130': date_create
                }
            }

            data_for_company = {
                "entityTypeId": 185,
                "id": apartment_id,
                "fields": {
                    "ufCrm9_1684774043": new_balance
                }
            }

            try:
                deal_response = await self.add_deal(payload=data_for_deal)
                deal_id = deal_response.get("result")

                if not deal_id:
                    raise Exception("Bitrix не вернул ID созданной сделки")
            except Exception as ex:
                raise Exception("Не удалось создать сделку по запросу из Каспи") from ex

            try:
                await self.update_apartment(payload=data_for_company)
            except Exception as ex:
                await self.delete_deal(deal_id=deal_id)
                raise Exception("Не удалось обновить квартиру по запросу из Каспи — сделка удалена") from ex

            data_for_comment = {
                "fields": {
                    'ENTITY_TYPE': "dynamic_185",
                    'ENTITY_ID': apartment_id,
                    'COMMENT': f"Создана сделка по пополнению: https://domcet.bitrix24.kz/crm/deal/details/{deal_id}/. Сумма пополнения: {summ}"
                }
            }

            try:
                await self.add_comment(payload=data_for_comment)
            except Exception as ex:
                raise Exception("Не удалось добавить комментарий для квартиры по сделке Каспи") from ex
        except Exception as ex:
            raise ex
        