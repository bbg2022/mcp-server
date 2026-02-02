import json
import os
import urllib.parse
import urllib.request

import bytedance.context

CONSOLE_ACTION_MAP = {
    "McpDescribeCdnConfig": {
        "method": "POST",
        "action": "DescribeCdnConfig",
        "version": "2021-03-01",
    },
}


class AIPaaSAPI:
    def request(self, action_key: str, params: dict, body_json: str, meta: dict | None) -> str:
        info = CONSOLE_ACTION_MAP.get(action_key, {})
        if not info:
            raise ValueError(f"Missing console action config for {action_key}")
        method = info.get("method")
        action = info.get("action")
        version = info.get("version")
        if not method or not action or not version:
            raise ValueError(
                f"Incomplete console action config for {action_key}: {info}"
            )
        region = get_volcengine_region(meta)
        base_url = get_console_api_base_url(meta)
        url = f"{base_url}/api/top/CDN/{region}/{version}/{action}"
        headers = get_console_headers()

        payload = body_json.encode("utf-8")
        if method.upper() == "GET":
            query = urllib.parse.urlencode(params or {})
            if query:
                url = f"{url}?{query}"
            payload = None
        request = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8")


_AIPAAS_API = AIPaaSAPI()


def console_request(action_key: str, body: dict) -> str:
    return _AIPAAS_API.request(action_key, {}, json.dumps(body), body.get("_meta"))


def get_console_api_base_url(meta: dict | None) -> str:
    if isinstance(meta, dict):
        meta_base_url = meta.get("API_BASE_URL")
        if isinstance(meta_base_url, str) and meta_base_url.strip():
            return meta_base_url.strip().rstrip("/")
    raise ValueError("Missing API_BASE_URL in _meta")


def get_volcengine_region(meta: dict | None) -> str:
    if isinstance(meta, dict):
        meta_region = meta.get("REGION")
        if isinstance(meta_region, str) and meta_region.strip():
            return meta_region.strip()
    raise ValueError("Missing REGION in _meta")


def get_console_headers() -> dict:
    headers = {}
    request_headers = bytedance.context.get("mcp_headers") or {}
    for key in (
        "cookie",
        "x-csrf-token",
        "x-tt-logid",
        "x-requested-with",
        "referer",
        "user-agent",
    ):
        if key in request_headers:
            headers[key] = request_headers[key]
    headers.setdefault("content-type", "application/json")
    headers.setdefault("accept", "application/json")
    return headers


def is_console_jwt(meta: dict | None) -> bool:
    if not isinstance(meta, dict):
        return False
    return meta.get("REQUEST_MODE") == "console_jwt"
