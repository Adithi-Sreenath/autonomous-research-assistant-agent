import { ScrollArea } from "./ui/scroll-area";
import type { ActivityLog } from "@/app/hooks/useResearch";

interface ActivityFeedProps {
  activityLogs: ActivityLog[];
}

export const ActivityFeed = ({ activityLogs }: ActivityFeedProps) => {
  return (
    <div className="border border-primary/30 bg-card p-6">
      <h3 className="text-sm font-heading font-semibold text-primary mb-4 uppercase">
        Agent Activity Feed
      </h3>
      <ScrollArea className="h-[200px]">
        <div className="space-y-2 pr-4">
          {activityLogs.length === 0 ? (
            <div className="text-xs font-mono text-muted-foreground italic">
              No activity yet...
            </div>
          ) : (
            activityLogs.map((activity, i) => (
              <div key={i} className="flex gap-3 text-xs font-mono">
                <span className="text-muted-foreground">{activity.timestamp}</span>
                <span className="text-primary">[{activity.type}]</span>
                <span className="text-foreground/80">{activity.message}</span>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
};