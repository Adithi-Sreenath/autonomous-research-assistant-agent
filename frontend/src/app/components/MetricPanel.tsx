interface MetricPanelProps {
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
}

export const MetricPanel = ({ label, value, change, trend = "neutral" }: MetricPanelProps) => {
  const trendColors = {
    up: "text-primary",
    down: "text-accent",
    neutral: "text-muted-foreground",
  };

  return (
    <div className="border border-primary/30 bg-card p-4">
      <div className="text-xs text-muted-foreground font-mono uppercase mb-2">
        {label}
      </div>
      <div className="flex items-end justify-between">
        <div className="text-2xl font-heading font-bold">{value}</div>
        {change && (
          <div className={`text-xs font-mono ${trendColors[trend]}`}>
            {change}
          </div>
        )}
      </div>
    </div>
  );
};
