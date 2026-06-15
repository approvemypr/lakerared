import asyncio
import os
import sys

from lakera_red_sdk import (
    LakeraRedClient,
    ReconContext,
    CrescendoStrategyOptions,
)
from agent_client import AgentClient


async def main():
    async with LakeraRedClient(
        api_key=os.environ["red_key"],
        base_url="https://red-webhooks.lakera.ai",
        log_level="info",
    ) as client:
        scan = await client.create_scan(
            name=f"Jenkins DAST #{os.environ.get('BUILD_NUMBER', 'local')}",
            target="my-agent",
            app_context_file="./app-context.yaml",
            strategy=CrescendoStrategyOptions(max_turns=15),
            objectives=[
                "security.instruction-override.1",
                ],
            concurrency=3,
        )

        print(f"Scan attributes: {vars(scan)}")

        async def handler(session):
            agent = AgentClient(
                base_url=os.environ["TARGET_AGENT_URL"],
                api_key=os.environ.get("TARGET_AGENT_API_KEY"),
            )
            try:
                async for message in session:
                    reply = await agent.chat(message.attack)
                    await message.respond(reply)
            finally:
                await agent.shutdown()

        await scan.run(handler)

        results = await scan.get_results()
        await scan.write_results("./red-results.json")

        issues = [r for r in (results.results or []) if r.evaluation]
        print(f"Issues found: {len(issues)}")

        threshold = int(os.environ.get("RED_FAIL_THRESHOLD", "0"))
        if len(issues) > threshold:
            print(f"FAIL: {len(issues)} issues exceed threshold {threshold}",
                  file=sys.stderr)
            sys.exit(1)


asyncio.run(main())
