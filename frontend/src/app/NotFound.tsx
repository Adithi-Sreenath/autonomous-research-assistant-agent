import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { AlertCircle } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 border border-primary/30 bg-primary/5 mb-6">
          <AlertCircle className="w-8 h-8 text-primary" />
        </div>
        <h1 className="mb-4 text-6xl font-heading font-bold">404</h1>
        <p className="mb-8 text-lg text-muted-foreground">ROUTE NOT FOUND</p>
        <a 
          href="/" 
          className="inline-block px-6 py-3 border border-primary/30 bg-primary/10 hover:bg-primary/20 transition-colors font-mono text-sm"
        >
          RETURN TO LAB
        </a>
      </div>
    </div>
  );
};

export default NotFound;
