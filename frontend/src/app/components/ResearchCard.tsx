import { LucideIcon } from "lucide-react";
import { ReactNode } from "react";

interface ResearchCardProps {
  title: string;
  icon: LucideIcon;
  value: string | number;
  description?: string;
  status?: "active" | "idle" | "processing";
  children?: ReactNode;
}

export const ResearchCard = ({ 
  title, 
  icon: Icon, 
  value, 
  description,
  status = "idle",
  children 
}: ResearchCardProps) => {
  const statusColors = {
    active: "text-primary",
    idle: "text-muted-foreground",
    processing: "text-accent",
  };

  return (
    <div className="border border-primary/30 bg-card p-6 hover:border-primary/60 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 border border-primary/30 bg-primary/5">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-heading text-sm font-semibold">{title}</h3>
            {description && (
              <p className="text-xs text-muted-foreground mt-1">{description}</p>
            )}
          </div>
        </div>
        <span className={`text-xs font-mono uppercase ${statusColors[status]}`}>
          {status}
        </span>
      </div>
      
      <div className="mt-4">
        <div className="text-3xl font-heading font-bold">{value}</div>
        {children}
      </div>
    </div>
  );
};
