"use client";

import { Brain, BookOpen, HelpCircle, Beaker, Database, BarChart3, Users, FileText } from "lucide-react";
import { NavLink } from "./NavLink";
import type { StageStatus } from "@/app/hooks/useResearch";

interface SidebarProps {
  stageStatuses: Map<string, StageStatus>;
  isConnected: boolean;
  messagesCount: number;
}

const navigation = [
  { name: "Topic Understanding", icon: Brain, path: "/", stage: "Topic Understanding" },
  { name: "Literature Review", icon: BookOpen, path: "/literature", stage: "Literature Review" },
  { name: "Research Question", icon: HelpCircle, path: "/question", stage: "Research Question" },
  { name: "Methodology", icon: Beaker, path: "/methodology", stage: "Methodology" },
  { name: "Data Collection", icon: Database, path: "/collection", stage: "Data Collection" },
  { name: "Data Analysis", icon: BarChart3, path: "/analysis", stage: "Data Analysis" },
  { name: "Multi-Agent Discussion", icon: Users, path: "/discussion", stage: "Multi-Agent Discussion" },
  { name: "Final Paper", icon: FileText, path: "/paper", stage: "Final Paper" },
];

export const Sidebar = ({ stageStatuses, isConnected, messagesCount }: SidebarProps) => {
  const getStageStatus = (stage: string) => {
    return stageStatuses.get(stage);
  };

  const getStatusIndicator = (stage: string) => {
    const status = getStageStatus(stage);
    if (!status) return null;

    const colors = {
      pending: "bg-muted-foreground/30",
      running: "bg-accent animate-pulse",
      completed: "bg-primary",
      failed: "bg-destructive",
    };

    return (
      <span className={`w-2 h-2 rounded-full ${colors[status.status]}`} />
    );
  };

  return (
    <aside className="w-64 border-r border-primary/30 flex flex-col h-screen">
      <div className="p-6 border-b border-primary/30">
        <h1 className="text-2xl font-heading font-bold text-primary">
          AI LAB
        </h1>
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          v2.5.0 // RESEARCH
        </p>
      </div>
      
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            href={item.path}
            className="flex items-center gap-3 px-4 py-3 text-sm transition-colors border border-transparent hover:border-primary/30 hover:bg-primary/5"
            activeClassName="border-primary bg-primary/10"
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium flex-1">{item.name}</span>
            {getStatusIndicator(item.stage)}
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-primary/30">
        <div className="text-xs font-mono space-y-1">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Status</span>
            <span className={isConnected ? "text-primary" : "text-destructive"}>
              {isConnected ? "ACTIVE" : "OFFLINE"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Messages</span>
            <span className="text-foreground">{messagesCount}</span>
          </div>
        </div>
      </div>
    </aside>
  );
};