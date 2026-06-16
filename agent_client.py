import httpx


class AgentClient:
    """调用被测 n8n agent 的 HTTP 客户端。"""

    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 60.0):
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    async def chat(self, prompt: str) -> str:
        resp = await self._client.post(
            "",                          # base_url 已是完整 webhook 地址
            json={"message": prompt},    # n8n 期望的输入字段
        )
        resp.raise_for_status()
        data = resp.json()
        # n8n 把回复放在 "message" 字段
        return data["message"]

    async def shutdown(self):
        await self._client.aclose()
