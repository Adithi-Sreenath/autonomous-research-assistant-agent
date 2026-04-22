# discussion_multiagent.py
from agent_template import BaseAgent
from utils import compact_context
import json
import re


async def run_multiagent_discussion_async(analysis_text: str):
    """
    Fully async multi-agent discussion.
    ALL agent calls use _call_async() ONLY.
    NEVER use .run() inside an asyncio environment.
    """

    # ---- Create agents ----
    analyst = BaseAgent(
        name="result_analyst",
        system_prompt=(
            "Interpret research results concisely. Identify key findings only."
        ),
    )

    critic = BaseAgent(
        name="critic",
        system_prompt=(
            "Identify limitations in the interpretation. Keep critique short and specific."
        ),
    )

    synthesizer = BaseAgent(
        name="synthesizer",
        system_prompt=(
            "Merge discussion into JSON with keys: interpretation, implications, "
            "limitations, future_work. Output ONLY JSON."
        ),
    )

    print("[Discussion] Starting compact multi-agent negotiation...")

    # ---- TURN 1: Analyst ----
    print("  → Analyst: Interpreting results...")
    interpretation_v1 = await analyst._call_async(
        compact_context(analysis_text, max_tokens=400)
    )

    # ---- TURN 2: Critic ----
    print("  → Critic: Reviewing interpretation...")
    critique = await critic._call_async(
        compact_context(interpretation_v1, max_tokens=350)
    )

    # ---- TURN 3: Analyst Refines ----
    print("  → Analyst: Refining interpretation...")
    interpretation_v2 = await analyst._call_async(
        f"Refine using critique:\n{compact_context(critique, 300)}\n\n"
        f"Original:\n{compact_context(analysis_text, 400)}"
    )

    # ---- TURN 4: Synthesizer ----
    print("  → Synthesizer: Producing JSON summary...")
    raw_json = await synthesizer._call_async(
        f"""
Combine into JSON:
INTERPRETATION_1: {compact_context(interpretation_v1, 150)}
CRITIQUE: {compact_context(critique, 150)}
INTERPRETATION_2: {compact_context(interpretation_v2, 150)}

Return ONLY JSON with keys:
interpretation, implications, limitations, future_work
"""
    )

    # ---- Extract JSON safely ----
    match = re.search(r"\{.*\}", raw_json, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    # safe fallback
    return {
        "interpretation": interpretation_v2[:200],
        "implications": "",
        "limitations": critique[:200],
        "future_work": "",
    }
