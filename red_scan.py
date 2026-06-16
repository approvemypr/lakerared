import asyncio
import os
import sys
from lakera_red_sdk import (
    LakeraRedClient,
    ReconContext,
    CrescendoStrategyOptions,
)
from agent_client import AgentClient


# 覆盖 support 提供的全部 objective
ALL_OBJECTIVES = [
    # Security
    "security.instruction-override.1",
    "security.system-prompt-extraction.1",
    "security.tool-extraction.1",
    "security.data-exfiltration.1",
    # Safety
    "safety.hate-speech.1",
    "safety.violence-extremism.1",
    "safety.cbrne.1",
    "safety.self-harm.1",
    "safety.sexual-content.1",
    "safety.harassment-bullying.1",
    "safety.dangerous-instructions.1",
    "safety.drug-synthesis.1",
    # Responsible
    "responsible.misinformation.1",
    "responsible.copyright-infringement.1",
    "responsible.fraud-facilitation.1",
    "responsible.criminal-advice.1",
    "responsible.brand-damaging.1",
    "responsible.unauthorized-discounts.1",
    "responsible.discrimination-bias.1",
    "responsible.specialized-advice.1",
    "responsible.defamation-libel.1",
    "responsible.hallucination.1",
    "responsible.cybercrime-facilitation.1",
]


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
            objectives=ALL_OBJECTIVES,
            concurrency=3,
        )
        print(f"Scan progress: https://red.lakera.ai/scans/{scan.scan_id}/progress")

        async def handler(session):
            agent = AgentClient(
                base_url=os.environ["TARGET_AGENT_URL"],
                api_key=os.environ.get("app_key"),
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
