import os
import httpx


class AgentClient:
    """调用被测 agent 的 HTTP 客户端。"""

    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 60.0):
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        # 注意: 不要禁用 TLS 校验
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    async def chat(self, prompt: str) -> str:
        # 按你 agent 的真实接口调整 path / 请求体 / 响应字段
        resp = await self._client.post(
            "",
            json={"message": prompt},
        )
        resp.raise_for_status()
        data = resp.json()
        # 按真实响应结构提取文本
        return data["reply"]

    async def shutdown(self):
        await self._client.aclose()
