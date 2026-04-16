# api_server.py
"""
FastAPI backend that connects your Research Agent Assistant to the Next.js frontend.
Provides REST endpoints and WebSocket for real-time streaming.
"""
from utils import compact_context
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
import json
import uuid
import re
from datetime import datetime
import os

# Import your pipeline
from coordinator import CoordinatorAgent
from pipeline import (
    run_discussion_stage,
    run_finalization_stage,
    build_stage_agents
)
from discussion_multiagent import run_multiagent_discussion_async as run_multiagent_discussion_async
# Import Groq error handling
try:
    from groq import RateLimitError
except Exception:
    # Fallback if groq doesn't export RateLimitError directly
    class RateLimitError(Exception):
        pass

app = FastAPI(title="Research Agent Assistant API", version="2.5.0")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Data Models ====================

class ResearchRequest(BaseModel):
    topic: str
    use_multiagent_discussion: bool = False

class PipelineStatus(BaseModel):
    session_id: str
    status: str  # "running", "completed", "failed"
    current_stage: str
    progress: int  # 0-100
    timestamp: str

# ==================== Global State ====================

active_sessions: Dict[str, Dict[str, Any]] = {}

# ==================== Helper Functions ====================

async def handle_rate_limit_error(websocket: WebSocket, error: Exception):
    """
    Gracefully handle rate limit errors by notifying the user
    and providing helpful information.
    """
    error_message = str(error)
    wait_match = re.search(r'try again in (\d+)m(\d+)', error_message)
    if wait_match:
        minutes = wait_match.group(1)
        seconds = wait_match.group(2)
        wait_time = f"{minutes} minutes {seconds} seconds"
    else:
        wait_time = "a few minutes"

    await websocket.send_json({
        "type": "ERROR",
        "message": f"⏱️ Rate Limit Reached\n\nGroq API rate limit exceeded. Please wait {wait_time} before trying again.\n\n💡 Options:\n1. Wait for rate limit reset\n2. Switch to llama-3.1-8b-instant model (higher limits)\n3. Upgrade your Groq tier at console.groq.com",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    await send_activity_log(
        websocket,
        "SYSTEM",
        "💡 TIP: Use a smaller model for testing (llama-3.1-8b-instant has much higher rate limits)"
    )

async def send_agent_message(websocket: WebSocket, agent_name: str, message: str, msg_type: str = "AGENT"):
    """Send formatted message to WebSocket client"""
    await websocket.send_json({
        "type": msg_type,
        "agent": agent_name,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

async def send_status_update(websocket: WebSocket, stage: str, status: str, details: str = ""):
    """Send status update to client"""
    await websocket.send_json({
        "type": "STATUS",
        "stage": stage,
        "status": status,
        "details": details,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

async def send_activity_log(websocket: WebSocket, activity_type: str, message: str):
    """Send activity log entry"""
    await websocket.send_json({
        "type": "ACTIVITY",
        "activity_type": activity_type,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {
        "service": "Research Agent Assistant API",
        "version": "2.5.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "start_research": "POST /api/research/start",
            "websocket": "WS /ws/{session_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/research/start")
async def start_research(request: ResearchRequest):
    """Initialize a new research session"""
    session_id = str(uuid.uuid4())

    active_sessions[session_id] = {
        "topic": request.topic,
        "status": "initialized",
        "created_at": datetime.now().isoformat(),
        "use_multiagent": request.use_multiagent_discussion
    }

    return {
        "session_id": session_id,
        "status": "initialized",
        "websocket_url": f"ws://localhost:8000/ws/{session_id}"
    }

@app.get("/api/research/status/{session_id}")
async def get_research_status(session_id: str):
    """Get current status of research session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return active_sessions[session_id]

# ==================== WebSocket for Streaming ====================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time pipeline execution streaming.
    Sends agent outputs, status updates, and activity logs to frontend.
    """
    await websocket.accept()

    if session_id not in active_sessions:
        await websocket.send_json({"error": "Invalid session ID"})
        await websocket.close()
        return

    session = active_sessions[session_id]
    topic = session["topic"]

    try:
        await send_agent_message(websocket, "SYSTEM", "Agent network initialized", "SYSTEM")
        await send_agent_message(websocket, "SYSTEM", f"Session started for topic: {topic}", "SYSTEM")
        await send_activity_log(websocket, "SYSTEM", "Session started")

        # ==================== Stage 1-6: Initial Pipeline ====================

        await send_status_update(websocket, "Topic Understanding", "running", "Analyzing research topic...")

        coordinator = CoordinatorAgent()

        # Custom pipeline execution with streaming
        await execute_pipeline_with_streaming(websocket, topic, coordinator, session)

        # ==================== Stage 7: Discussion ====================
        await send_status_update(websocket, "Multi-Agent Discussion", "running", "Synthesizing findings...")
        await send_activity_log(websocket, "TOPIC", "Discussion synthesis started")

        # Import async version
        

        # Run discussion directly (async)
        pipeline_state = session.get("pipeline_state", {})

        # robust retrieval of analysis text (consumer-side fallback)
        analysis_text = None
        if pipeline_state.get("analysis"):
            analysis_text = pipeline_state.get("analysis")
        elif pipeline_state.get("data_analysis"):
            analysis_text = pipeline_state.get("data_analysis")
        elif pipeline_state:
            # fallback: last stage output (should be safe because producer sets canonical alias,
            # but we keep consumer fallback as extra safety)
            last_key = list(pipeline_state.keys())[-1]
            analysis_text = pipeline_state.get(last_key)

        if not analysis_text:
            await send_agent_message(websocket, "SYSTEM", "No analysis output found from pipeline; aborting discussion stage.", "ERROR")
            session["status"] = "failed"
            return

        discussion_json = await run_multiagent_discussion_async(analysis_text)

        # guard: ensure discussion_json has expected fields
        interpretation = discussion_json.get("interpretation") if isinstance(discussion_json, dict) else None
        if not interpretation:
            await send_agent_message(websocket, "Discussion Synthesizer", "Discussion returned no interpretation, proceeding with best effort.", "AGENT")
        else:
            await send_agent_message(
                websocket,
                "Discussion Synthesizer",
                f"Interpretation: {interpretation[:200]}..." if isinstance(interpretation, str) else "Interpretation produced.",
                "AGENT"
            )

        await send_status_update(websocket, "Multi-Agent Discussion", "completed")

        # ==================== Stage 8: Finalization ====================
        await send_status_update(websocket, "Final Paper", "running", "Generating final paper...")
        await send_activity_log(websocket, "SYSTEM", "Finalizing research paper")

        # Run finalization in executor
        loop = asyncio.get_event_loop()
        final = await loop.run_in_executor(
            None,
            run_finalization_stage,
            session["pipeline_state"],
            discussion_json
        )

        # Send final paper (defensive access)
        final_content = final.get("final") if isinstance(final, dict) else None
        final_conclusion = final.get("conclusion") if isinstance(final, dict) else None

        await websocket.send_json({
            "type": "FINAL_PAPER",
            "content": final_content or "",
            "conclusion": final_conclusion or "",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        await send_status_update(websocket, "Final Paper", "completed")
        await send_agent_message(websocket, "SYSTEM", "Research paper generation complete!", "SYSTEM")

        session["status"] = "completed"

    except RateLimitError as e:
        # Handle rate limit gracefully
        print(f"⏱️ Rate limit hit: {str(e)}")
        await handle_rate_limit_error(websocket, e)
        session["status"] = "rate_limited"

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error in websocket: {str(e)}")
        import traceback
        traceback.print_exc()
        await send_agent_message(websocket, "SYSTEM", f"Error: {str(e)}", "ERROR")
        session["status"] = "failed"
    finally:
        try:
            await websocket.close()
        except:
            pass


async def execute_pipeline_with_streaming(websocket: WebSocket, topic: str, coordinator, session):
    """
    Execute the initial pipeline with streaming output to WebSocket.
    This is a modified version of run_initial_pipeline() that sends updates.
    """
    A = build_stage_agents()

    stages = [
        ("Topic Understanding", A["topic"], topic, "Refined topic, subtopics, research questions, hypotheses."),
        ("Literature Review", A["literature"], None, "Summarized literature, key studies, gaps."),
        ("Research Question", A["question"], None, "Numbered research questions and hypotheses."),
        ("Methodology", A["method"], None, "Approach, data needs, variables, procedures, ethics."),
        ("Data Collection", A["collect"], None, "Plan, sources, instrumentation, sample, simulated_schema."),
        ("Data Analysis", A["analyze"], None, "Methods used, results, figures/stats summary, caveats.")
    ]

    pipeline_state = {}
    context = topic

    for stage_name, agent, input_override, expected in stages:
        await send_status_update(websocket, stage_name, "running", f"Processing {stage_name}...")
        await send_activity_log(websocket, "TOPIC", f"Processing {stage_name}")

        # Use context or override
        stage_input = input_override if input_override else context

        # Run stage with revision (this handles the coordinator loop)
        output, evaluation = await run_stage_with_revision_async(
            agent, stage_input, coordinator, expected, websocket, stage_name
        )

        # Store in pipeline state
        stage_key = stage_name.lower().replace(" ", "_")
        pipeline_state[stage_key] = output

        # Update context for next stage
        context = output

        # Send completion
        await send_status_update(websocket, stage_name, "completed")
        await send_agent_message(websocket, agent.name, f"Stage complete: {output[:150]}...", "AGENT")

    # ==================== Producer-side canonical aliasing ====================
    # Ensure 'analysis' canonical key exists for downstream consumers
    if "analysis" not in pipeline_state:
        if "data_analysis" in pipeline_state:
            pipeline_state["analysis"] = pipeline_state["data_analysis"]
        elif pipeline_state:
            # fallback: last stage output becomes 'analysis' (should be data_analysis normally)
            last_key = list(pipeline_state.keys())[-1]
            pipeline_state["analysis"] = pipeline_state[last_key]

    # Save pipeline state into session
    session["pipeline_state"] = pipeline_state

# In run_stage_with_revision_async, update the revision_prompt:
async def run_stage_with_revision_async(agent, input_payload, coordinator, expected, websocket, stage_name, max_rounds=2):
    loop = asyncio.get_event_loop()

    try:
        # Run agent in executor (non-blocking)
        output = await loop.run_in_executor(None, agent.run, input_payload)

        # Run coordinator in executor (non-blocking)
        evaluation = await loop.run_in_executor(
            None,
            lambda: coordinator.run(stage_output=output, expected_output=expected)
        )

        round_num = 0
        while evaluation.get("action") == "revise" and round_num < max_rounds:
            await send_activity_log(
                websocket,
                "SYSTEM",
                f"Revision needed: {evaluation.get('reason', 'Quality improvement required')[:100]}"
            )

            # ✨ COMPACT THE PROMPTS TO AVOID TOKEN LIMITS
            revision_prompt = f"""
Previous output was insufficient. Here's the evaluation:

REASON FOR REVISION:
{compact_context(evaluation.get('reason', ''), 300)}

SPECIFIC INSTRUCTIONS:
{compact_context(evaluation.get('revision_instructions', ''), 300)}

ORIGINAL INPUT (summary):
{compact_context(input_payload, 600)}

Please provide an IMPROVED version that addresses the issues above.
"""

            # Run revision in executor
            output = await loop.run_in_executor(
                None,
                lambda: agent.run(revision_prompt, use_memory=False)  # ← Disable memory to save tokens
            )

            # Evaluate revision in executor
            evaluation = await loop.run_in_executor(
                None,
                lambda: coordinator.run(stage_output=output, expected_output=expected)
            )
            round_num += 1

        if evaluation.get("action") == "revise":
            await send_activity_log(websocket, "SYSTEM", "Max revisions reached. Accepting best effort.")

        return compact_context(output, max_tokens=800), evaluation


    except Exception as e:
        print(f"Error in stage {stage_name}: {str(e)}")
        await send_activity_log(websocket, "SYSTEM", f"Error in {stage_name}: {str(e)[:100]}")
        raise e

# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
