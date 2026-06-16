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
            "",
            json={"message": prompt},
        )
        resp.raise_for_status()

        text = resp.text
        if not text.strip():
            # 空响应：打印诊断信息后返回空串，避免 JSONDecodeError 中断整个 session
            print(f"[agent_client] EMPTY response. status={resp.status_code} "
                  f"headers={dict(resp.headers)}")
            return ""

        try:
            data = resp.json()
        except Exception:
            # 非 JSON：打印原始内容，按纯文本返回
            print(f"[agent_client] NON-JSON response. status={resp.status_code} "
                  f"body={text[:500]!r}")
            return text

        # 兼容 message / output / reply 等常见字段
        for key in ("message", "output", "reply", "text"):
            if isinstance(data, dict) and key in data:
                return str(data[key])

        # 字典里没找到预期字段，整体转字符串返回并打印
        print(f"[agent_client] No known reply field. data={data!r}")
        return str(data)

    async def shutdown(self):
        await self._client.aclose()
