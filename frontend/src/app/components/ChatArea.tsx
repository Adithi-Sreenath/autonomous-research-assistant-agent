import { ScrollArea } from "./ui/scroll-area";
import { useEffect, useRef } from "react";
import type { AgentMessage } from "@/app/hooks/useResearch";

interface ChatAreaProps {
  messages: AgentMessage[];
  finalPaper: string | null;
  error: string | null;
}

export const ChatArea = ({ messages, finalPaper, error }: ChatAreaProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="w-full px-8 py-6 border-b border-primary/30">
      <div className="max-w-5xl mx-auto">
        <ScrollArea className="h-[280px] border border-primary/30 bg-black/50">
          <div className="p-6 space-y-6" ref={scrollRef}>
            {messages.length === 0 && !error && (
              <div className="text-center text-muted-foreground font-mono text-sm py-12">
                Enter a research topic to begin...
              </div>
            )}

            {messages.map((message, i) => {
              const isUser = message.type === "USER";
              const isSystem = message.type === "SYSTEM";
              const isAgent = message.type === "AGENT";
              const isStatus = message.type === "STATUS";

              // Skip STATUS messages (shown in sidebar instead)
              if (isStatus) return null;

              return (
                <div
                  key={i}
                  className={`flex gap-4 ${
                    isUser ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] ${
                      isUser
                        ? "bg-primary/10 border border-primary/40"
                        : isSystem
                        ? "bg-accent/10 border border-accent/40"
                        : "bg-card border border-primary/30"
                    } p-4`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`text-xs font-mono uppercase ${
                          isUser
                            ? "text-accent"
                            : isSystem
                            ? "text-accent"
                            : "text-primary"
                        }`}
                      >
                        [{message.agent || message.type}]
                      </span>
                      {message.timestamp && (
                        <span className="text-xs font-mono text-muted-foreground">
                          {message.timestamp}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-foreground/90 font-mono leading-relaxed whitespace-pre-wrap">
                      {message.message}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Error Display */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/40 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono uppercase text-destructive">
                    [ERROR]
                  </span>
                </div>
                <div className="text-sm text-destructive/90 font-mono">
                  {error}
                </div>
              </div>
            )}

            {/* Final Paper Display */}
            {finalPaper && (
              <div className="bg-primary/5 border border-primary/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono uppercase text-primary">
                      [FINAL PAPER]
                    </span>
                  </div>
                  <button
                    onClick={() => {
                      const blob = new Blob([finalPaper], { type: "text/plain" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = "research_paper.txt";
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="text-xs font-mono text-primary hover:text-accent transition-colors border border-primary/30 px-3 py-1 hover:border-accent"
                  >
                    DOWNLOAD
                  </button>
                </div>
                <div className="text-sm text-foreground/90 font-mono leading-relaxed whitespace-pre-wrap max-h-[400px] overflow-y-auto">
                  {finalPaper}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};