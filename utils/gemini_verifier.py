import json
import os
from typing import Any, Dict

import google.generativeai as genai
import streamlit as st


class GeminiMatchVerifier:
    def __init__(self) -> None:
        api_key = ""
        try:
            api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        except Exception:
            api_key = ""
        if not api_key:
            api_key = str(os.environ.get("GEMINI_API_KEY", "")).strip()

        self.enabled = bool(api_key)
        if self.enabled:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    @staticmethod
    def _default_result(reason: str) -> Dict[str, Any]:
        return {"is_match": False, "confidence": 0, "reason": reason}

    @staticmethod
    def _safe_parse_json(raw_text: str) -> Dict[str, Any]:
        txt = str(raw_text or "").strip()
        if not txt:
            return {"is_match": False, "confidence": 0, "reason": "empty response"}

        # Handle accidental wrappers like ```json ... ```
        txt = txt.replace("```json", "").replace("```", "").strip()
        start = txt.find("{")
        end = txt.rfind("}")
        if start != -1 and end != -1 and end > start:
            txt = txt[start : end + 1]

        try:
            obj = json.loads(txt)
        except Exception:
            return {"is_match": False, "confidence": 0, "reason": "invalid json response"}

        is_match = bool(obj.get("is_match", False))
        conf = obj.get("confidence", 0)
        try:
            conf = int(float(conf))
        except Exception:
            conf = 0
        conf = max(0, min(100, conf))
        reason = str(obj.get("reason", "") or "").strip()[:300]
        if not reason:
            reason = "no reason returned"
        return {"is_match": is_match, "confidence": conf, "reason": reason}

    def verify_perfume_match(self, mahwous_name: str, comp_name: str) -> Dict[str, Any]:
        if not self.enabled or self.model is None:
            return self._default_result("gemini api key not configured")

        prompt = f"""
You are a Master Perfume Expert.
Compare these two product names and decide if they are the EXACT same perfume product.

Rules:
1) Must match same brand and same perfume line/flanker.
2) Must match concentration/type exactly (EDP, EDT, Parfum, Extrait, Cologne, Intense, etc.).
3) Consider edition hints (limited, tester, gift set, refill, body mist) as different products.
4) If uncertain, return is_match=false.

Mahwous product name: "{mahwous_name}"
Competitor product name: "{comp_name}"

Output strictly as raw JSON only (no markdown, no backticks), exactly in this schema:
{{"is_match": true, "confidence": 95, "reason": "brief explanation"}}
"""
        try:
            resp = self.model.generate_content(prompt)
            raw_text = getattr(resp, "text", "") if resp is not None else ""
            return self._safe_parse_json(raw_text)
        except Exception as e:
            return self._default_result(f"gemini error: {str(e)[:160]}")

