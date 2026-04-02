import { Button } from "./ui/button";

interface ActionsPanelProps {
  isRunning: boolean;
  onStop: () => void;
  onRunMultiAgent: () => void;
  onGeneratePaper: () => void;
}

export const ActionsPanel = ({ 
  isRunning, 
  onStop, 
  onRunMultiAgent, 
  onGeneratePaper 
}: ActionsPanelProps) => {
  return (
    <div className="border border-primary/30 bg-card p-6">
      <h3 className="text-sm font-heading font-semibold text-primary mb-4 uppercase">
        Actions
      </h3>
      <div className="space-y-3">
        <Button 
          onClick={onStop}
          disabled={!isRunning}
          variant="outline" 
          className="w-full justify-start border-destructive/50 text-destructive hover:border-destructive hover:bg-destructive/10 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Stop Research
        </Button>
        <Button 
          onClick={onRunMultiAgent}
          disabled={isRunning}
          variant="outline"
          className="w-full justify-start border-primary/30 hover:border-primary hover:bg-primary/5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Run Multi-Agent Discussion
        </Button>
        <Button 
          onClick={onGeneratePaper}
          disabled={isRunning}
          variant="outline"
          className="w-full justify-start border-primary/30 hover:border-primary hover:bg-primary/5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Generate Final Paper
        </Button>
      </div>
    </div>
  );
};
