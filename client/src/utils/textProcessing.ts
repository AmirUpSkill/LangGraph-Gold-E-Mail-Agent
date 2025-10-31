// ============================================================
// UTILITY: Text Processing
// ============================================================
// Handles text cleaning and extraction operations
// - Remove XML thinking tags from AI output
// - Extract JSON from markdown code blocks
// - Parse wrapped JSON responses
// ============================================================

// --- Remove Think Tags ---
// Strips <think>...</think> tags and their content from text
export const removeThinkTags = (text: string): string => {
  return text.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
};

// --- Extract JSON from Markdown ---
// Removes markdown code block syntax (```json ... ```)
export const stripMarkdownCodeBlocks = (text: string): string => {
  return text
    .replace(/^```json\s*\n?/i, '')
    .replace(/\n?```\s*$/i, '')
    .trim();
};

// --- Parse JSON Wrapper ---
// Attempts to parse JSON-wrapped content and extract email/reasoning
export const parseJsonWrapper = (content: string): { 
  email?: string; 
  reasoning?: string; 
  parsed: boolean;
} => {
  const cleanContent = stripMarkdownCodeBlocks(content);
  
  try {
    const parsed = JSON.parse(cleanContent);
    return {
      email: parsed.final_email,
      reasoning: parsed.reasoning,
      parsed: true,
    };
  } catch {
    return {
      email: cleanContent,
      parsed: false,
    };
  }
};
