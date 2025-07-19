"use client";

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  contentType?: 'general' | 'question' | 'answer'; // Unified content type handling
  enhanceFormatting?: boolean;
}

/**
 * General content preprocessing for readability improvements
 */
function preprocessGeneral(content: string): string {
  let processed = content;
  
  // Handle inline numbered sections (e.g., "1. Cost Efficiency: - Open Source:")
  processed = processed.replace(/(\d+)\.\s*([^:]+):\s*-\s*/g, '\n\n$1. **$2:**\n   - ');
  
  // Convert numbered items with colons to proper headers (e.g., "1. Cost Efficiency:")
  processed = processed.replace(/^\s*(\d+)\.\s*([^:]+):\s*/gm, '\n\n$1. **$2:**\n\n');
  
  // Convert numbered items without colons to proper markdown lists
  processed = processed.replace(/^\s*(\d+)\.\s+([^:]+)$/gm, '$1. $2');
  
  // Handle sub-bullet points with different symbols
  processed = processed.replace(/^\s*[-•*~]\s*([^:]+):\s*/gm, '   - **$1:** ');
  processed = processed.replace(/^\s*[-•*~]\s+(.+)$/gm, '   - $1');
  
  // Convert lettered lists (a. b. c.) to sub-bullets
  processed = processed.replace(/^\s*([a-z])\.\s+(.+)$/gm, '   - $2');
  
  // Convert parenthetical numbered items to sub-bullets
  processed = processed.replace(/^\s*\(?\d+\)\s+(.+)$/gm, '   - $1');
  
  // Handle complex patterns like "- Proprietary: Usually entails..."
  processed = processed.replace(/^\s*-\s*([A-Z][^:]{1,30}):\s*/gm, '   - **$1:** ');
  
  // Handle section headers (e.g., "Strategic Approach:")
  processed = processed.replace(/^([A-Z][^:]{5,50}):\s*-\s*/gm, '\n\n## $1\n\n- ');
  
  // Convert "Answer:" or "Response:" to bold
  processed = processed.replace(/^(Answer|Response|Solution):\s*/gm, '**$1:** ');
  
  // Handle step-by-step patterns
  processed = processed.replace(/^(Step \d+):\s*/gm, '**$1:** ');
  
  // Convert ordinal transitions to bold
  processed = processed.replace(/^(First|Second|Third|Fourth|Fifth|Finally|Lastly|In conclusion),?\s*/gm, '**$1:** ');
  
  // Handle special terms and concepts
  processed = processed.replace(/^(Integrating Insights):\s*/gm, '\n\n## $1\n\n');
  
  // Ensure proper line breaks between main sections
  processed = processed.replace(/([.!?])\s*([A-Z][^.]{10,}:)/g, '$1\n\n$2');
  
  // Fix sentences that should be separate paragraphs (longer content)
  processed = processed.replace(/(\w)\.\s*([A-Z][^.]{25,}[.!?])\s*([A-Z])/g, '$1.\n\n$2\n\n$3');
  
  // Handle question patterns - ensure questions end paragraphs
  processed = processed.replace(/(\w\?)\s+([A-Z])/g, '$1\n\n$2');
  
  // Convert "Note:" or "Important:" to highlighted text
  processed = processed.replace(/^(Note|Important|Warning|Tip|In summary):\s*/gm, '> **$1:** ');
  
  // Handle key-value patterns for definitions
  processed = processed.replace(/^([A-Z][A-Za-z\s]{2,30}):\s*([^-].{10,}[.!?])/gm, '**$1:** $2');
  
  // Clean up excessive spacing around lists
  processed = processed.replace(/([.!?])\s*\n\s*(\d+\.|[-•*])\s+/g, '$1\n\n$2 ');
  
  // Ensure proper spacing between sections
  processed = processed.replace(/\n{4,}/g, '\n\n\n');
  processed = processed.replace(/([.!?])\n{1,2}(\d+\.|##)/g, '$1\n\n$2');
  
  return processed.trim();
}

/**
 * Question-specific preprocessing
 */
function preprocessQuestion(content: string): string {
  let processed = content;
  
  // Ensure question ends with question mark if it's clearly a question
  if (processed.match(/^(what|how|why|when|where|which|who|does|do|did|can|could|would|should|will|is|are|was|were)/i) && !processed.endsWith('?')) {
    processed = processed.trim() + '?';
  }
  
  // Handle multi-part questions
  processed = processed.replace(/\?\s*([A-Z][^?]*?)$/g, '?\n\n$1?');
  
  // Format question parts with numbers or letters
  processed = processed.replace(/^(\d+\.|[a-z]\)|\([a-z]\))\s*/gm, '**$1** ');
  
  return processed;
}

/**
 * Answer-specific preprocessing with enhanced formatting
 */
function preprocessAnswer(content: string): string {
  let processed = content;
  
  // STEP 1: Handle stage-specific patterns (e.g., "For Early-Stage Adoption: - Prioritization:")
  processed = processed.replace(/\b(For\s+[A-Z][A-Za-z\s-]+):\s*-\s*([A-Z][^:]+):\s*/g, '\n\n## $1\n\n- **$2:** ');
  
  // STEP 2: Handle complex inline patterns (e.g., "1. Cost Efficiency: - Open Source:")
  processed = processed.replace(/(\d+)\.\s*([^:]+):\s*-\s*([A-Z][^:]+):\s*/g, '\n\n$1. **$2:**\n   - **$3:** ');
  
  // STEP 3: Handle continuation patterns within sections (e.g., "- Strategies:" after "- Prioritization:")
  processed = processed.replace(/\.\s*-\s*([A-Z][A-Za-z\s]+):\s*/g, '.\n\n- **$1:** ');
  
  // STEP 4: Handle standalone numbered sections with colons (e.g., "1. Cost Efficiency:")
  processed = processed.replace(/^\s*(\d+)\.\s*([^:]+):\s*$/gm, '\n\n$1. **$2:**\n\n');
  
  // STEP 5: Handle section headers that end with colons (e.g., "Strategic Approach:")
  processed = processed.replace(/^([A-Z][A-Za-z\s]{8,50}):\s*-\s*/gm, '\n\n## $1\n\n- ');
  processed = processed.replace(/^([A-Z][A-Za-z\s]{8,50}):\s*$/gm, '\n\n## $1\n\n');
  
  // STEP 6: Handle standalone sub-points with dashes and colons (e.g., "- Organizations should...")
  processed = processed.replace(/^\s*-\s*([A-Z][^:]{10,})\.\s*/gm, '   - $1.\n\n');
  processed = processed.replace(/^\s*-\s*([A-Z][^:]{3,30}):\s*/gm, '   - **$1:** ');
  
  // STEP 7: Clean up numbered list formatting
  processed = processed.replace(/^(\d+)\.\s*([^:]+)$/gm, '$1. $2');
  
  // STEP 8: Handle transition words and phrases
  processed = processed.replace(/\.\s*(Because|Since|Therefore|However|Moreover|Furthermore|Additionally),?\s+/g, '.\n\n$1, ');
  
  // STEP 9: Handle examples with proper formatting
  processed = processed.replace(/\.\s*(For example|For instance|Such as),?\s+/g, '.\n\n**$1:** ');
  
  // STEP 10: Handle conclusions and summaries (including standalone "Overall,")
  processed = processed.replace(/\.\s*(In conclusion|To summarize|In summary|Finally),?\s+/g, '.\n\n**$1:** ');
  processed = processed.replace(/\.\s*(Overall),\s+/g, '.\n\n**$1:** ');
  
  // STEP 11: Make key evaluation terms bold
  processed = processed.replace(/\b(essential|key point|important note|remember|crucial|critical|typically|usually|often)\b/gi, '**$1**');
  
  // STEP 12: Handle sentence breaks that should become paragraph breaks
  processed = processed.replace(/([.!?])\s+([A-Z][a-z])/g, '$1\n\n$2');
  
  // STEP 13: Clean up excessive spacing
  processed = processed.replace(/\n{4,}/g, '\n\n\n');
  processed = processed.replace(/\n{3}/g, '\n\n');
  
  return processed;
}

/**
 * Main preprocessing function that routes to content-type-specific processors
 */
function preprocessContent(content: string, contentType: 'general' | 'question' | 'answer'): string {
  switch (contentType) {
    case 'question':
      return preprocessQuestion(content);
    case 'answer':
      return preprocessAnswer(content);
    case 'general':
    default:
      return preprocessGeneral(content);
  }
}

export default function MarkdownRenderer({ 
  content, 
  className = "", 
  contentType = 'general',
  enhanceFormatting = true 
}: MarkdownRendererProps) {
  // Apply content-type-specific preprocessing if enhancement is enabled
  const processedContent = enhanceFormatting ? preprocessContent(content, contentType) : content;
  
  // Content-type-specific CSS classes
  const contentTypeClasses = {
    question: "question-content font-medium",
    answer: "answer-content", 
    general: "general-content"
  };
  
  return (
    <div className={`markdown-content ${contentTypeClasses[contentType]} ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headers with improved spacing
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-primary-700 mb-4 mt-6 first:mt-0 border-b border-primary-200 pb-2">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-primary-700 mb-3 mt-5 first:mt-0">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-medium text-primary-700 mb-2 mt-4 first:mt-0">{children}</h3>
          ),
          
          // Enhanced paragraphs with better spacing and typography
          p: ({ children }) => (
            <p className="text-primary-700 mb-3 last:mb-0 leading-relaxed text-sm">{children}</p>
          ),
          
          // Enhanced lists with better styling
          ul: ({ children }) => (
            <ul className="list-disc ml-5 text-primary-700 mb-3 space-y-1.5 [&_ul]:list-[circle] [&_ul]:ml-4 [&_ul]:mt-1 [&_ul]:mb-1">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal ml-5 text-primary-700 mb-3 space-y-1.5 [&_ol]:list-[lower-alpha] [&_ol]:ml-4 [&_ol]:mt-1 [&_ol]:mb-1">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="text-primary-700 text-sm leading-relaxed pl-1">{children}</li>
          ),
          
          // Code with better contrast
          code: ({ children, ...props }) => {
            const inline = !props.className?.includes('language-');
            return inline ? (
              <code className="bg-primary-200/60 text-primary-900 px-1.5 py-0.5 rounded text-sm font-mono border border-primary-300/50">
                {children}
              </code>
            ) : (
              <code className="block bg-primary-100/70 text-primary-900 p-4 rounded-lg text-sm font-mono overflow-x-auto mb-3 border border-primary-200">
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-primary-100/70 text-primary-900 p-4 rounded-lg text-sm font-mono overflow-x-auto mb-3 border border-primary-200">
              {children}
            </pre>
          ),
          
          // Enhanced links
          a: ({ href, children }) => (
            <a 
              href={href} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-500 underline underline-offset-2 decoration-primary-400 hover:decoration-primary-500 transition-colors"
            >
              {children}
            </a>
          ),
          
          // Enhanced emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-primary-800">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-primary-700 font-medium">{children}</em>
          ),
          
          // Enhanced blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary-400 pl-4 py-2 bg-primary-50/50 rounded-r-lg mb-3 italic text-primary-700">
              {children}
            </blockquote>
          ),
          
          // Enhanced tables
          table: ({ children }) => (
            <div className="overflow-x-auto mb-3">
              <table className="w-full border-collapse border border-primary-200 text-sm rounded-lg overflow-hidden">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-primary-100/70">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="border border-primary-200 px-3 py-2 text-left font-semibold text-primary-800">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-primary-200 px-3 py-2 text-primary-700">
              {children}
            </td>
          ),
          
          // Enhanced horizontal rule
          hr: () => (
            <hr className="border-primary-300 my-6 border-t-2" />
          ),
          
          // Line breaks
          br: () => <br className="mb-1" />,
        }}
      >
        {processedContent}
      </ReactMarkdown>
      
      {/* Content-type-specific styling */}
      <style jsx>{`
        .question-content :global(.markdown-content p) {
          font-size: 0.95rem;
          line-height: 1.6;
          color: rgb(55, 65, 81);
        }
        
        .answer-content :global(.markdown-content p) {
          font-size: 0.875rem;
          line-height: 1.7;
          margin-bottom: 1rem;
        }
        
        .answer-content :global(.markdown-content li) {
          margin-bottom: 0.5rem;
          padding-left: 0.25rem;
        }
        
        .answer-content :global(.markdown-content ul),
        .answer-content :global(.markdown-content ol) {
          margin-top: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .markdown-content :global(.markdown-content blockquote) {
          background: linear-gradient(135deg, rgb(239, 246, 255) 0%, rgb(219, 234, 254) 100%);
          border-left-color: rgb(59, 130, 246);
          font-style: normal;
          font-weight: 500;
        }
        
        .markdown-content :global(.markdown-content strong) {
          color: rgb(30, 64, 175);
          font-weight: 600;
        }
      `}</style>
    </div>
  );
} 