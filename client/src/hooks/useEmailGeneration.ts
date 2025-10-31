// ============================================================
// HOOK: Email Generation Manager
// ============================================================
// Manages the entire email generation lifecycle including:
// - Form state (job URL, resume file)
// - API communication with backend
// - Progress tracking synchronized with request stages
// - Error handling and user notifications
// ============================================================

import { useState, useCallback } from "react";
import { toast } from "@/hooks/use-toast";
import type { EmailGenerationResponse } from "@/types/api";

// --- Configuration ---
const API_ENDPOINT = "http://localhost:8000/generate-email";
const REQUEST_TIMEOUT = 120000; // 2 minutes
const PROGRESS_UPDATE_INTERVAL = 500; // 0.5 seconds
const ESTIMATED_PROCESSING_TIME = 45000; // 45 seconds estimate

// --- Progress Stage Definitions ---
const PROGRESS_STAGES = {
  PREPARE: 5,
  SEND: 10,
  SEND_COMPLETE: 20,
  PROCESSING_START: 20,
  PROCESSING_END: 80,
  RESPONSE_RECEIVED: 85,
  PARSING: 90,
  PRE_COMPLETE: 95,
  COMPLETE: 100,
} as const;

export const useEmailGeneration = () => {
  // --- State Management ---
  const [jobUrl, setJobUrl] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<EmailGenerationResponse | null>(null);
  const [progress, setProgress] = useState(0);

  // --- File Validation ---
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ];
    
    if (!validTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF or DOCX file",
        variant: "destructive",
      });
      return;
    }
    
    if (file.size > 20 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Maximum file size is 20MB",
        variant: "destructive",
      });
      return;
    }
    
    setResume(file);
  }, []);

  // --- Clear Form ---
  const handleClear = useCallback(() => {
    setJobUrl("");
    setResume(null);
    setResult(null);
    setProgress(0);
  }, []);

  // --- Progress Tracker ---
  const startProgressTracking = (startTime: number) => {
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const calculatedProgress = Math.min(
        PROGRESS_STAGES.PROCESSING_END,
        PROGRESS_STAGES.PROCESSING_START + 
          (elapsed / ESTIMATED_PROCESSING_TIME) * 
          (PROGRESS_STAGES.PROCESSING_END - PROGRESS_STAGES.PROCESSING_START)
      );
      setProgress(calculatedProgress);
    }, PROGRESS_UPDATE_INTERVAL);

    return interval;
  };

  // --- API Request Handler ---
  const handleGenerate = useCallback(async () => {
    // --- Input Validation ---
    if (!jobUrl || !resume) {
      toast({
        title: "Missing information",
        description: "Please provide both job URL and resume",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    setResult(null);
    setProgress(0);

    const startTime = Date.now();
    let progressInterval: NodeJS.Timeout | null = null;

    try {
      // --- Stage 1: Prepare Request (0-10%) ---
      setProgress(PROGRESS_STAGES.PREPARE);
      const formData = new FormData();
      formData.append("job_url", jobUrl);
      formData.append("resume", resume);
      
      setProgress(PROGRESS_STAGES.SEND);
      
      // --- Stage 2: Send Request (10-20%) ---
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
      
      const responsePromise = fetch(API_ENDPOINT, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });
      
      setProgress(PROGRESS_STAGES.SEND_COMPLETE);
      
      // --- Stage 3: Processing (20-80%) ---
      progressInterval = startProgressTracking(startTime);

      const response = await responsePromise;
      clearTimeout(timeoutId);
      if (progressInterval) clearInterval(progressInterval);
      
      setProgress(PROGRESS_STAGES.RESPONSE_RECEIVED);

      if (!response.ok) {
        throw new Error("Failed to generate email");
      }

      // --- Stage 4: Parse Response (85-95%) ---
      setProgress(PROGRESS_STAGES.PARSING);
      const data: EmailGenerationResponse = await response.json();
      
      // --- Stage 5: Complete (95-100%) ---
      setProgress(PROGRESS_STAGES.PRE_COMPLETE);
      setResult(data);
      
      setTimeout(() => {
        setProgress(PROGRESS_STAGES.COMPLETE);
        toast({
          title: "Email generated!",
          description: "Your personalized cold email is ready",
        });
      }, 300);
      
    } catch (error) {
      if (progressInterval) clearInterval(progressInterval);
      setProgress(0);
      toast({
        title: "Generation failed",
        description: error instanceof Error ? error.message : "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  }, [jobUrl, resume]);

  return {
    // State
    jobUrl,
    resume,
    isGenerating,
    result,
    progress,
    // Actions
    setJobUrl,
    handleFileChange,
    handleClear,
    handleGenerate,
  };
};
