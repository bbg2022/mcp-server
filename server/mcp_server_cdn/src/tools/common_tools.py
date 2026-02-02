import json
from src.CDN.api.api import CdnAPI
from src.utils.response import HandlerVolcResponse
from src.utils.mcp_console_request import AIPaaSAPI, is_console_jwt
from src.tools.tool_descriptions import DESCRIBE_CDN_CONFIG_DESCRIPTION


def describe_cdn_config(body: dict) -> str:
    meta = body.get("_meta")
    if meta is not None:
        print(f"describe_cdn_config _meta: {meta}")
    if is_console_jwt(meta):
        faasService = AIPaaSAPI()
        reqs = faasService.request(
            "McpDescribeCdnConfig", {}, json.dumps(body), meta
        )
        return reqs

    service = CdnAPI()
    reqs = service.mcp_post("McpDescribeCdnConfig", {}, json.dumps(body))

    return HandlerVolcResponse(reqs)


describe_cdn_config.__doc__ = DESCRIBE_CDN_CONFIG_DESCRIPTION
