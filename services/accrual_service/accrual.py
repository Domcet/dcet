from dcet_tools.http_requests import bx24_post_request
import datetime
from services.accrual_service.config import *
from dcet_tools.exception_decorator import catch_exception
from dcet_tools.dcet_logging import BaseLogging
from services.accrual_service.apartment import Apartment
import pandas as pd
import datetime
import pytz


class Accrual:
    months = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    tz = pytz.timezone("Asia/Qyzylorda") 
    now = datetime.datetime.now(tz)
    print(now)
    if now.month == 1:
        log_month = months[11]
        log_year = now.year - 1
    else:
        log_month = months[now.month - 2]
        log_year = now.year

    logger_name_static = f"Начисление {log_month} {log_year}.log"
    deal_name_static = f"Начисление за {log_month} {log_year}"

    def __init__(self):
        self.logger = BaseLogging(self.logger_name_static)

    async def _get_all_apartments(self):
        self.logger.info(f"Началось начисление за {self.log_month} {self.log_year}. Время начала: {self.now}")

        params = {
            'entityTypeId': apartment_entityTypeId,
            'filter': {
                is_accrual: 1
            },
            'select': [title, balance, id_, rate, exemption]
        }

        response = await bx24_post_request("crm.item.list.json", params)
        length = response.get('total', 0)

        out = []
        count = 0

        for i in range(0, length, 50):
            params['start'] = i
            res = await bx24_post_request("crm.item.list.json", params)
            items = res.get('result', {}).get('items', [])

            for item in items:
                deal = await Apartment(item, self.deal_name_static)._get_deal_by_title(self.deal_name_static)
                if deal is False:
                    out.append(item)

            count += 1
            self.logger.info(f"Получена пачка квартир (50 штук): {count}")

        self.logger.info(f"Квартиры для начисления: {len(out)}")

        if not out:
            raise Exception("Начисление уже выполнено.")
        return out
    
    async def make_report(self, out, processed_apartments, deal_name):
        """
        Создает или обновляет отчет в формате Excel с информацией о начислениях.
        Отчет формируется и дополняется сразу после обработки каждой квартиры.
        
        :param out: список квартир, которые не получили начисление
        :param processed_apartments: список квартир, которые успешно прошли начисление
        """
        filename = f"{deal_name}.xlsx"
        
        # Проверяем, есть ли уже существующий файл отчета
        try:
            existing_df = pd.read_excel(filename)
            data = existing_df.to_dict(orient='records')
        except FileNotFoundError:
            data = []

        processed_ids = {apt["id"] for apt in processed_apartments} 

        for apt in processed_apartments:
            data.append({
                "ID квартиры": apt["id"],
                "Название": apt["title"],
                "Старый баланс": apt["ufCrm9_1684774043"],
                "Новый баланс": apt["new_balance"],
                "Статус начисления": "Успешно"
            })

        for apt in out:
            if apt["id"] not in processed_ids:
                data.append({
                    "ID квартиры": apt["id"],
                    "Название": apt["title"],
                    "Старый баланс": apt["ufCrm9_1684774043"],
                    "Новый баланс": "Не изменился",
                    "Статус начисления": "Не начислено"
                })

        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        
        print(f"Отчет обновлен: {filename}")
        return filename

    @catch_exception(logger_name_static)
    async def run(self, deal_name):
        deal = deal_name if deal_name else self.deal_name_static
        all_apartments = await self._get_all_apartments()
        processed_apartments = []

        for apartment in all_apartments:
            try:
                new_balance = await Apartment(
                    apartment_data=apartment,
                    deal_name=deal
                ).do_sync_accrual(self.logger)

                apartment["new_balance"] = new_balance  
                processed_apartments.append(apartment)
                
                await self.make_report([apartment], processed_apartments, deal)
                
            except Exception as ex:
                raise ex        
            