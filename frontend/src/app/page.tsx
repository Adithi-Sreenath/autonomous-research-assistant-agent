"use client";

import { useState } from "react";
import { Sidebar } from "@/app/components/Sidebar";
import { HeroSphere } from "@/app/components/HeroSphere";
import { TopicPanel } from "@/app/components/TopicPanel";
import { ActivityFeed } from "@/app/components/ActivityFeed";
import { ActionsPanel } from "@/app/components/ActionsPanel";
import { ChatArea } from "./components/ChatArea";
import { InputBar } from "./components/InputBar";
import { useResearch } from "@/app/hooks/useResearch";

export default function Page() {
  const {
    isConnected,
    isRunning,
    messages,
    activityLogs,
    stageStatuses,
    finalPaper,
    error,
    startResearch,
    stopResearch,
  } = useResearch();

  const [topic, setTopic] = useState("");

  const handleInitiate = async () => {
    if (topic.trim() && !isRunning) {
      await startResearch(topic, false); // false = single-agent mode
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar fixed on left - pass stage statuses */}
      <div className="w-64 border-r border-primary/30">
        <Sidebar stageStatuses={stageStatuses} isConnected={isConnected} messagesCount={messages.length} />
      </div>

      {/* Right content scrolls independently */}
      <main className="flex-1 overflow-y-auto">
        {/* Hero */}
        <section className="border-b border-primary/30">
          <HeroSphere />

          <div className="text-center pb-4 px-8">
            <h2 className="text-3xl font-heading font-bold mb-1">
              Autonomous Research Assistant
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto font-mono text-xs">
              Human-in-the-Loop • Multi-Agent Reasoning • Transparent Scientific Outputs
            </p>
          </div>

          {/* Chat Area - pass messages */}
          <ChatArea messages={messages} finalPaper={finalPaper} error={error} />

          {/* Input Bar - pass handlers */}
          <InputBar 
            topic={topic}
            setTopic={setTopic}
            onInitiate={handleInitiate}
            isRunning={isRunning}
          />
        </section>

        {/* Panels */}
        <section className="px-12 py-12">
          <div className="grid grid-cols-3 gap-6">
            <TopicPanel />
            <ActivityFeed activityLogs={activityLogs} />
            <ActionsPanel 
              isRunning={isRunning}
              onStop={stopResearch}
              onRunMultiAgent={() => {/* TODO */}}
              onGeneratePaper={() => {/* TODO */}}
            />
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-primary/30 py-6 px-12">
          <div className="flex items-center justify-between text-xs font-mono text-muted-foreground">
            <div>SYSTEM v2.5.0 // Build 20250106</div>
            <div className={isConnected ? "text-primary" : "text-destructive"}>
              {isConnected ? "All systems operational" : "Disconnected"}
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}