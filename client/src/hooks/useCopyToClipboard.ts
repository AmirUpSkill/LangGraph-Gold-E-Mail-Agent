// ============================================================
// HOOK: Copy to Clipboard
// ============================================================
// Reusable clipboard functionality with visual feedback
// - Copies text to clipboard
// - Manages copied state with auto-reset
// - Shows toast notification
// ============================================================

import { useState, useCallback } from "react";
import { toast } from "@/hooks/use-toast";

const RESET_DELAY = 2000; // 2 seconds

export const useCopyToClipboard = () => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = useCallback((text: string, label?: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    
    toast({
      title: "Copied to clipboard",
      description: label ? `${label} copied successfully` : "Content copied successfully",
    });
    
    setTimeout(() => setCopied(false), RESET_DELAY);
  }, []);

  return { copied, copyToClipboard };
};
