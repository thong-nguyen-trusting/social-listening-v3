from __future__ import annotations

import re


class PIIMasker:
    PATTERNS = [
        (re.compile(r"\b0\d{9,10}\b"), "[PHONE]"),
        (re.compile(r"\b\d{9,12}\b"), "[ID_NUMBER]"),
        (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    ]

    def mask(self, text: str) -> str:
        masked = text
        for pattern, replacement in self.PATTERNS:
            masked = pattern.sub(replacement, masked)
        return masked
