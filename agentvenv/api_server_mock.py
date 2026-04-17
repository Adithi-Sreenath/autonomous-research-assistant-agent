# api_server_mock.py
"""
Mock version of API server that simulates the research pipeline
WITHOUT making any LLM API calls. Perfect for:
- Testing frontend integration
- Developing UI features
- Demoing without rate limits
- Working while waiting for rate limit reset
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any

app = FastAPI(title="Research Agent Assistant API (MOCK MODE)", version="2.5.0-mock")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Data Models ====================

class ResearchRequest(BaseModel):
    topic: str
    use_multiagent_discussion: bool = False

active_sessions: Dict[str, Dict[str, Any]] = {}

# ==================== Mock Data ====================

MOCK_STAGES = [
    {
        "name": "Topic Understanding",
        "agent": "topic_understanding_agent",
        "duration": 2,
        "output": """**Topic Analysis Complete**

Breaking down the research scope:

• **Core Concepts**: Identified 4 primary domains
• **Research Questions**: Formulated 3 specific questions
• **Academic Depth**: Sufficient for publication-level research
• **Scope Parameters**: Defined boundaries and constraints

Proceeding to literature review phase..."""
    },
    {
        "name": "Literature Review",
        "agent": "literature_review_agent",
        "duration": 3,
        "output": """**Literature Survey Complete**

Key Findings:
• Reviewed 47 peer-reviewed articles
• Identified 3 major research gaps
• Found 12 highly-cited foundational papers
• Mapped theoretical frameworks

Current consensus suggests further investigation needed in methodology."""
    },
    {
        "name": "Research Question",
        "agent": "research_question_agent",
        "duration": 2,
        "output": """**Research Questions Formulated**

RQ1: What is the primary relationship between X and Y?
RQ2: How do contextual factors influence outcomes?
RQ3: What are the long-term implications?

Hypotheses:
H1: Variable X positively correlates with outcome Y
H2: Contextual factor Z moderates the relationship"""
    },
    {
        "name": "Methodology",
        "agent": "methodology_agent",
        "duration": 3,
        "output": """**Methodology Designed**

Approach: Mixed-methods research design
• Quantitative: Survey (n=500)
• Qualitative: Semi-structured interviews (n=30)
• Data triangulation for validation
• Statistical analysis: Regression + thematic coding"""
    },
    {
        "name": "Data Collection",
        "agent": "data_collection_agent",
        "duration": 2,
        "output": """**Data Collection Plan**

Sources:
• Primary: Surveys and interviews
• Secondary: Existing datasets
• Sampling: Stratified random sampling
• Timeline: 8 weeks collection period
• Quality controls: Pilot testing + validation"""
    },
    {
        "name": "Data Analysis",
        "agent": "data_analysis_agent",
        "duration": 3,
        "output": """**Analysis Complete**

Results:
• Significant correlation found (r=0.68, p<0.001)
• Effect size: Cohen's d = 0.72 (medium-large)
• Qualitative themes: 5 major patterns emerged
• Model explains 54% of variance (R²=0.54)"""
    },
    {
        "name": "Multi-Agent Discussion",
        "agent": "discussion_synthesizer",
        "duration": 2,
        "output": """**Discussion Synthesis**

Interpretation: Results support initial hypotheses with moderate effect sizes
Implications: Findings suggest practical applications in field
Limitations: Sample bias and generalizability concerns noted
Future Work: Longitudinal studies recommended"""
    },
    {
        "name": "Final Paper",
        "agent": "quality_control_agent",
        "duration": 2,
        "output": """# Research Paper: [Your Topic]

## Abstract
This study investigates the relationship between key variables using a mixed-methods approach...

## Introduction
Recent developments in the field have highlighted...

## Literature Review
Existing research suggests...

## Methodology
We employed a mixed-methods design...

## Results
Analysis revealed significant findings...

## Discussion
Our results indicate...

## Conclusion
This research contributes to the field by...

## References
[Generated citations would appear here]"""
    }
]

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {
        "service": "Research Agent Assistant API (MOCK MODE)",
        "version": "2.5.0-mock",
        "note": "This is a mock server that simulates the research pipeline without making LLM API calls",
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
        "mode": "MOCK",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/research/start")
async def start_research(request: ResearchRequest):
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
        "websocket_url": f"ws://localhost:8000/ws/{session_id}",
        "mode": "MOCK"
    }

# ==================== WebSocket Mock ====================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.send_json({"error": "Invalid session ID"})
        await websocket.close()
        return
    
    session = active_sessions[session_id]
    topic = session["topic"]
    
    try:
        # Initial system message
        await websocket.send_json({
            "type": "SYSTEM",
            "message": f"🎭 MOCK MODE: Simulating research pipeline for '{topic}'",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        await asyncio.sleep(0.5)
        
        await websocket.send_json({
            "type": "SYSTEM",
            "message": "Agent network initialized (mock)",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Simulate each stage
        for stage_idx, stage in enumerate(MOCK_STAGES):
            # Send stage start
            await websocket.send_json({
                "type": "STATUS",
                "stage": stage["name"],
                "status": "running",
                "details": f"Processing {stage['name']}...",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Send activity log
            await websocket.send_json({
                "type": "ACTIVITY",
                "activity_type": "SYSTEM",
                "message": f"{stage['name']} started",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Simulate processing time
            await asyncio.sleep(stage["duration"])
            
            # Simulate occasional revision (for stage 2 and 4)
            if stage_idx in [1, 3]:
                await websocket.send_json({
                    "type": "ACTIVITY",
                    "activity_type": "SYSTEM",
                    "message": f"Revision requested: Adding more detail",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                await asyncio.sleep(1)
            
            # Send agent output
            await websocket.send_json({
                "type": "AGENT",
                "agent": stage["agent"],
                "message": stage["output"],
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Send activity log
            await websocket.send_json({
                "type": "ACTIVITY",
                "activity_type": "TOPIC",
                "message": f"{stage['name']} completed",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Send stage complete
            await websocket.send_json({
                "type": "STATUS",
                "stage": stage["name"],
                "status": "completed",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            await asyncio.sleep(0.5)
        
        # Send final paper
        await websocket.send_json({
            "type": "FINAL_PAPER",
            "content": f"""# Research Paper: {topic}

## Abstract
This mock research paper demonstrates the complete pipeline output. In production mode, this would contain actual LLM-generated research content based on your topic.

## Introduction
The field of {topic} has seen significant developments in recent years. This study investigates key aspects through a rigorous mixed-methods approach.

## Literature Review
Previous research has established several important findings. We identified three major themes:
1. Theoretical frameworks
2. Empirical evidence
3. Research gaps

## Methodology
We employed a mixed-methods design combining:
- Quantitative surveys (n=500)
- Qualitative interviews (n=30)
- Statistical analysis using regression models

## Results
Our analysis revealed:
- Significant correlation (r=0.68, p<0.001)
- Medium-large effect size (Cohen's d=0.72)
- Five emergent qualitative themes

## Discussion
These findings suggest important implications for both theory and practice. The results support our initial hypotheses while revealing unexpected patterns in the data.

## Limitations
- Sample bias considerations
- Generalizability constraints
- Temporal limitations

## Conclusion
This research contributes to the field by providing empirical evidence for theoretical claims. Future studies should investigate longitudinal effects.

## References
Mock Reference 1 (2024). Title of Paper. Journal Name.
Mock Reference 2 (2023). Another Title. Conference Proceedings.

---
**Note**: This is a MOCK paper generated without LLM API calls. In production mode, real research content would be generated based on actual literature and analysis.
""",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Final system message
        await websocket.send_json({
            "type": "SYSTEM",
            "message": "✅ Research pipeline complete (mock mode)",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        session["status"] = "completed"
        
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "ERROR",
            "message": f"Mock error: {str(e)}",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🎭 MOCK MODE - Research Agent Assistant API")
    print("="*60)
    print("This server simulates the research pipeline without LLM calls")
    print("Perfect for testing frontend and UI development")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api_server_mock:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )