from aiogram.types import TelegramObject
from typing import Any, Dict

from aiogram.utils.i18n import I18nMiddleware


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        return 'ru'
