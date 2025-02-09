from aiogram.fsm.context import FSMContext
from templates import MessageTemplates
from typing import Dict, Any

def generate_profile_summary(data: Dict[str, Any]):
    return MessageTemplates.PROFILE_SUMMARY.format(**data)