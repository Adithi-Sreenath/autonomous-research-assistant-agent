export const TopicPanel = () => {
  return (
    <div className="border border-primary/30 bg-card p-6">
      <h3 className="text-sm font-heading font-semibold text-primary mb-4 uppercase">
        Topic Breakdown
      </h3>
      <div className="space-y-3 text-sm font-mono text-foreground/90">
        <div className="flex gap-3">
          <span className="text-primary">•</span>
          <span>Core concepts identified and structured</span>
        </div>
        <div className="flex gap-3">
          <span className="text-primary">•</span>
          <span>Key research domains mapped</span>
        </div>
        <div className="flex gap-3">
          <span className="text-primary">•</span>
          <span>Initial scope parameters defined</span>
        </div>
        <div className="flex gap-3">
          <span className="text-primary">•</span>
          <span>Conceptual framework established</span>
        </div>
      </div>
    </div>
  );
};
