from templates import SetProfileMessageTemplates
from typing import Dict, Any

def generate_profile_summary(data: Dict[str, Any]):
    return SetProfileMessageTemplates.PROFILE_SUMMARY.format(**data)

