// ============================================================
// PAGE: Cold Email Generator Index
// ============================================================
// Main application page handling:
// - User input form (job URL, resume upload)
// - Email generation workflow
// - Results visualization
// ============================================================

import { Upload, Zap, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import CanvasFlow from "@/components/CanvasFlow";
import { useEmailGeneration } from "@/hooks/useEmailGeneration";

const Index = () => {
  // --- Email Generation Hook ---
  const {
    jobUrl,
    resume,
    isGenerating,
    result,
    progress,
    setJobUrl,
    handleFileChange,
    handleClear,
    handleGenerate,
  } = useEmailGeneration();

  // --- Render ---
  return (
    <div className="min-h-screen bg-background relative overflow-hidden canvas-grid flex items-center justify-center">
      <div className="relative z-10 container mx-auto px-4 py-12">
        
        {/* --- Header Section --- */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 text-primary tracking-tight">
            Cold Email Generator
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your resume and job URL. Watch as three AI agents craft personalized emails, then synthesize the perfect pitch.
          </p>
        </div>

        {/* --- Input Form Section --- */}
        {!result && (
          <div className="max-w-2xl mx-auto mb-12 page-transition">
            <div className="card-3d bg-card rounded-2xl p-8">
              <div className="space-y-6">
                
                {/* Job URL Input */}
                <div className="space-y-2">
                  <Label htmlFor="jobUrl" className="text-foreground">Job URL</Label>
                  <Input
                    id="jobUrl"
                    type="url"
                    placeholder="https://jobs.lever.co/company/job-id"
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                    className="bg-secondary border-border focus:border-primary transition-colors text-foreground"
                  />
                </div>

                {/* Resume Upload */}
                <div className="space-y-2">
                  <Label htmlFor="resume" className="text-foreground">Resume (PDF or DOCX)</Label>
                  <div className="relative">
                    <Input
                      id="resume"
                      type="file"
                      accept=".pdf,.docx"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <label
                      htmlFor="resume"
                      className="flex items-center justify-center gap-2 w-full px-4 py-8 border-2 border-dashed border-border rounded-xl cursor-pointer hover:border-primary transition-colors bg-secondary/50"
                    >
                      <Upload className="w-5 h-5 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {resume ? resume.name : "Click to upload or drag and drop"}
                      </span>
                    </label>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 justify-end">
                  <Button
                    onClick={handleClear}
                    disabled={isGenerating}
                    className="bg-secondary hover:bg-secondary/80 text-secondary-foreground font-semibold px-6 py-6 text-base rounded-2xl shadow-[var(--shadow-3d)] hover:scale-[1.02] transition-all border-2 border-border"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Clear
                  </Button>
                  <Button
                    onClick={handleGenerate}
                    disabled={isGenerating || !jobUrl || !resume}
                    className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-8 py-6 text-base rounded-2xl shadow-[var(--shadow-3d)] hover:scale-[1.02] transition-all border-2 border-primary/30"
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    Generate
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* --- Results Visualization Section --- */}
        {(isGenerating || result) && (
          <div className="page-transition">
            <CanvasFlow isGenerating={isGenerating} result={result} progress={progress} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
