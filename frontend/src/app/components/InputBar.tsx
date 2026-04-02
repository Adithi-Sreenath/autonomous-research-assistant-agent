import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Dispatch, SetStateAction } from "react";

interface InputBarProps {
  topic: string;
  setTopic: Dispatch<SetStateAction<string>>;
  onInitiate: () => void;
  isRunning: boolean;
}

export const InputBar = ({ topic, setTopic, onInitiate, isRunning }: InputBarProps) => {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !isRunning && topic.trim()) {
      onInitiate();
    }
  };

  return (
    <div className="w-full px-8 py-6">
      <div className="max-w-5xl mx-auto flex gap-3">
        <Input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter research topic or command..."
          disabled={isRunning}
          className="flex-1 bg-black border border-primary font-mono text-sm text-foreground placeholder:text-[#CFC9E8] rounded-none h-12 px-4 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-primary disabled:opacity-50"
        />
        <Button
          onClick={onInitiate}
          disabled={isRunning || !topic.trim()}
          className="border border-primary bg-black text-primary hover:bg-accent hover:border-accent hover:text-black transition-all rounded-none h-12 px-6 font-heading uppercase text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunning ? "Running..." : "Initiate"}
        </Button>
      </div>
    </div>
  );
};
