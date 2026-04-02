import { useState, useEffect, useCallback, useRef } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export interface AgentMessage {
  type: "AGENT" | "SYSTEM" | "STATUS" | "ACTIVITY" | "FINAL_PAPER" | "ERROR" | "USER";
  agent?: string;
  message?: string;
  stage?: string;
  status?: string;
  details?: string;
  activity_type?: string;
  content?: string;
  conclusion?: string;
  timestamp: string;
}

export interface StageStatus {
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  timestamp?: string;
}

export interface ActivityLog {
  type: string;
  message: string;
  timestamp: string;
}

const STAGES = [
  "Topic Understanding",
  "Literature Review",
  "Research Question",
  "Methodology",
  "Data Collection",
  "Data Analysis",
  "Multi-Agent Discussion",
  "Final Paper",
];

// ===================================================================
//                🎯  FULLY REWRITTEN STABLE HOOK
// ===================================================================

export function useResearch() {
  const [isConnected, setIsConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [currentStage, setCurrentStage] = useState("");
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [stageStatuses, setStageStatuses] = useState<Map<string, StageStatus>>(new Map());
  const [finalPaper, setFinalPaper] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  // Initialize status map once
  useEffect(() => {
    const initial = new Map<string, StageStatus>();
    STAGES.forEach((stage) => initial.set(stage, { name: stage, status: "pending" }));
    setStageStatuses(initial);
  }, []);

  // ===================================================================
  //                     🎯 MESSAGE HANDLER
  // ===================================================================
  const handleMessage = useCallback((msg: AgentMessage) => {
    console.log("📨 WS Message:", msg);

    switch (msg.type) {
      case "AGENT":
      case "SYSTEM":
        setMessages((prev) => [...prev, msg]);
        break;

      case "STATUS":
        if (msg.stage && msg.status) {
          setCurrentStage(msg.stage);

          setStageStatuses((prev) => {
            const updated = new Map(prev);
            updated.set(msg.stage, {
              name: msg.stage,
              status: msg.status as any,
              timestamp: msg.timestamp,
            });
            return updated;
          });
        }
        break;

      case "ACTIVITY":
        if (msg.activity_type && msg.message) {
          setActivityLogs((prev) => [
            ...prev,
            { type: msg.activity_type, message: msg.message, timestamp: msg.timestamp },
          ]);
        }
        break;

      case "FINAL_PAPER":
        if (msg.content) {
          setFinalPaper(msg.content);
          setIsRunning(false);
        }
        break;

      case "ERROR":
        setError(msg.message || "Unknown error occurred");
        setIsRunning(false);
        break;
    }
  }, []);

  // ===================================================================
  //                     🎯 OPEN A NEW WEBSOCKET
  //     NO RECONNECT. NO DUPLICATION. CLEAN AND SAFE.
  // ===================================================================
  const openWebSocket = useCallback((sessionId: string) => {
    // Close previous socket safely
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const ws = new WebSocket(`${WS_BASE_URL}/ws/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
      setIsConnected(true);
    };

    ws.onmessage = (e) => {
      const msg: AgentMessage = JSON.parse(e.data);
      handleMessage(msg);
    };

    ws.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
      setError("WebSocket connection error");
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed by server");
      setIsConnected(false);
      setIsRunning(false);

      // ❗ No auto-reconnect because it causes multiple pipeline executions.
      // User must restart manually.
    };
  }, [handleMessage]);

  // ===================================================================
  //                 🎯 START A NEW RESEARCH SESSION
  // ===================================================================
  const startResearch = useCallback(
    async (topic: string, useMultiAgent = false) => {
      try {
        setError(null);
        setMessages([]);
        setActivityLogs([]);
        setFinalPaper(null);

        // Reset stage statuses
        const resetStatuses = new Map<string, StageStatus>();
        STAGES.forEach((stage) => resetStatuses.set(stage, { name: stage, status: "pending" }));
        setStageStatuses(resetStatuses);

        setIsRunning(true);

        // Start backend session
        const res = await fetch(`${API_BASE_URL}/api/research/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic, use_multiagent_discussion: useMultiAgent }),
        });

        if (!res.ok) throw new Error("Failed to start research session");

        const session = await res.json();
        sessionIdRef.current = session.session_id;

        // Add user query to UI
        setMessages([
          {
            type: "USER",
            message: topic,
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);

        // Open controlled WebSocket
        openWebSocket(session.session_id);
      } catch (err: any) {
        console.error("❌ Start Research Error:", err);
        setError(err.message || "Failed to start research");
        setIsRunning(false);
      }
    },
    [openWebSocket]
  );

  // ===================================================================
  //                         🎯 STOP SESSION
  // ===================================================================
  const stopResearch = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsRunning(false);
    setIsConnected(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return {
    isConnected,
    isRunning,
    currentStage,
    messages,
    activityLogs,
    stageStatuses,
    finalPaper,
    error,
    startResearch,
    stopResearch,
  };
}
