"use client";

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headers
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-primary-700 mb-3 mt-4 first:mt-0">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-primary-700 mb-2 mt-3 first:mt-0">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-medium text-primary-700 mb-2 mt-3 first:mt-0">{children}</h3>
          ),
          
          // Paragraphs
          p: ({ children }) => (
            <p className="text-primary-700 mb-2 last:mb-0 leading-relaxed">{children}</p>
          ),
          
          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-inside text-primary-700 mb-2 space-y-1">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside text-primary-700 mb-2 space-y-1">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="text-primary-700">{children}</li>
          ),
          
          // Code
          code: ({ children, ...props }) => {
            const inline = !props.className?.includes('language-');
            return inline ? (
              <code className="bg-primary-100/50 text-primary-800 px-1 py-0.5 rounded text-sm font-mono">
                {children}
              </code>
            ) : (
              <code className="block bg-primary-100/50 text-primary-800 p-3 rounded-lg text-sm font-mono overflow-x-auto mb-2">
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-primary-100/50 text-primary-800 p-3 rounded-lg text-sm font-mono overflow-x-auto mb-2">
              {children}
            </pre>
          ),
          
          // Links
          a: ({ href, children }) => (
            <a 
              href={href} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-500 underline"
            >
              {children}
            </a>
          ),
          
          // Emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-primary-800">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-primary-700">{children}</em>
          ),
          
          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary-300 pl-4 py-2 bg-primary-50/50 rounded-r-lg mb-2 italic text-primary-700">
              {children}
            </blockquote>
          ),
          
          // Tables
          table: ({ children }) => (
            <div className="overflow-x-auto mb-2">
              <table className="w-full border-collapse border border-primary-200 text-sm">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-primary-100/50">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="border border-primary-200 px-3 py-2 text-left font-medium text-primary-700">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-primary-200 px-3 py-2 text-primary-700">
              {children}
            </td>
          ),
          
          // Horizontal rule
          hr: () => (
            <hr className="border-primary-300 my-4" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
} 