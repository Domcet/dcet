from dcet_tools.base_configs import WEBHOOK_BITRIX_URL
import aiohttp
import asyncio


async def bx24_post_request(url, payload, delay=15, max_retries=30):
    normal_url = WEBHOOK_BITRIX_URL + str(url)
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        for attempt in range(max_retries):
            try:
                async with session.post(normal_url, json=payload, headers=headers) as response:
                    response_text = await response.text()

                    if response.status == 200:
                        try:
                            return await response.json()
                        except aiohttp.ContentTypeError:
                            raise Exception(f"Invalid JSON response: {response_text}")

                    elif 400 <= response.status < 500:
                        raise Exception(f"Client error {response.status}: {response_text}")

                    else:
                        await asyncio.sleep(delay)

            except aiohttp.ClientError as e:
                await asyncio.sleep(delay)

        raise Exception(f"Failed after {max_retries} attempts")


async def bx24_get_request(url, params, delay=2):
    normal_url = WEBHOOK_BITRIX_URL + str(url)
    headers = {
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(normal_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return (await response.json())['result']
                    else:
                        response_text = await response.text()
                        if 400 <= response.status < 500:  # Ошибка на стороне клиента (4xx)
                            error_text = f"Client error: {response.status} - {response_text}"
                            raise Exception(error_text)
                        else:
                            # Ошибка на стороне сервера или временная ошибка
                            await asyncio.sleep(delay)
            except Exception as e:
                # Обрабатываем сетевые или временные ошибки
                if isinstance(e, aiohttp.ClientError):
                    await asyncio.sleep(delay)
                else:
                    error_text = f"Failed to make request. {str(e)}"
                    raise Exception(error_text)
