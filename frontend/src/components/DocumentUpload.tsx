"use client";

import { useCallback, useState } from "react";
import { useDropzone, FileRejection } from "react-dropzone";
import { Upload, File, X, FileText, AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";
import { UploadedDocument, DocumentUploadProps } from "@/types";
import { extractFileContent } from "@/services/api";

export default function DocumentUpload({ documents, setDocuments, onNext }: DocumentUploadProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [textInput, setTextInput] = useState("");
  const [errors, setErrors] = useState<string[]>([]);

  const validateFile = (file: File): string | null => {
    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      return `${file.name}: File size exceeds 10MB limit`;
    }

    // Check file type
    const allowedTypes = ['text/plain', 'text/markdown', 'application/pdf'];
    const allowedExtensions = ['.txt', '.md', '.pdf'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      return `${file.name}: Unsupported file type. Please use PDF, TXT, or MD files`;
    }

    return null;
  };

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    setIsLoading(true);
    setErrors([]);
    
    const newErrors: string[] = [];
    const newDocuments: UploadedDocument[] = [];
    
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach((error) => {
        if (error.code === 'file-too-large') {
          newErrors.push(`${file.name}: File size exceeds 10MB limit`);
        } else if (error.code === 'file-invalid-type') {
          newErrors.push(`${file.name}: Unsupported file type`);
        } else {
          newErrors.push(`${file.name}: ${error.message}`);
        }
      });
    });

    // Check if adding these files would exceed the limit
    if (documents.length + acceptedFiles.length > 10) {
      newErrors.push(`Cannot upload more than 10 documents total. Currently have ${documents.length} documents.`);
      setErrors(newErrors);
      setIsLoading(false);
      return;
    }

    // Process accepted files
    for (const file of acceptedFiles) {
      const validationError = validateFile(file);
      if (validationError) {
        newErrors.push(validationError);
        continue;
      }

      try {
        let content = '';
        let extractedMetadata = {};
        
        if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
          // Extract PDF content using backend API
          console.log(`🔍 Extracting content from PDF: ${file.name}`);
          try {
            const extractionResult = await extractFileContent(file);
            
            if (extractionResult.success && extractionResult.data) {
              content = extractionResult.data.content;
              extractedMetadata = extractionResult.data.metadata;
              console.log(`✅ Successfully extracted ${extractionResult.data.metadata.content_length} characters from ${file.name}`);
            } else {
              throw new Error(extractionResult.error?.detail || 'PDF extraction failed');
            }
          } catch (error) {
            console.error('❌ PDF extraction error:', error);
            content = `[PDF File: ${file.name}] - Content extraction failed: ${error instanceof Error ? error.message : 'Unknown error'}`;
          }
        } else if (file.type === 'text/plain' || file.name.toLowerCase().endsWith('.txt') || file.name.toLowerCase().endsWith('.md')) {
          // Handle text files locally
          content = await file.text();
        } else {
          // Try to read as text for other file types
          try {
            content = await file.text();
          } catch {
            content = `[File: ${file.name}] - Could not extract text content`;
          }
        }

        const document: UploadedDocument = {
          id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          source: file.name,
          content: content,
          metadata: {
            filename: file.name,
            size: file.size,
            type: file.type,
            lastModified: file.lastModified,
            uploadedAt: new Date().toISOString(),
            ...extractedMetadata, // Include any metadata from backend extraction
          },
          size: file.size,
          type: file.type,
        };
        newDocuments.push(document);
      } catch {
        newErrors.push(`${file.name}: Failed to read file content`);
      }
    }
    
    if (newErrors.length > 0) {
      setErrors(newErrors);
    }

    if (newDocuments.length > 0) {
      setDocuments([...documents, ...newDocuments]);
    }
    
    setIsLoading(false);
  }, [documents, setDocuments]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 10,
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true,
  });

  const removeDocument = (id: string) => {
    setDocuments(documents.filter(doc => doc.id !== id));
    // Clear errors if we remove documents
    if (errors.some(error => error.includes('Cannot upload more than 10'))) {
      setErrors(errors.filter(error => !error.includes('Cannot upload more than 10')));
    }
  };

  const addTextDocument = () => {
    if (!textInput.trim()) return;

    if (documents.length >= 10) {
      setErrors(['Cannot upload more than 10 documents total']);
      return;
    }

    const document: UploadedDocument = {
      id: `text-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      source: 'manual-input',
      content: textInput.trim(),
      metadata: {
        type: 'manual',
        length: textInput.length,
        uploadedAt: new Date().toISOString(),
      },
      size: textInput.length,
      type: 'text/plain',
    };
    
    setDocuments([...documents, document]);
    setTextInput("");
    setErrors([]); // Clear errors on successful add
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const clearAllDocuments = () => {
    setDocuments([]);
    setErrors([]);
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-primary-700 mb-2">Upload Your Documents</h2>
        <p className="text-primary-700 max-w-2xl mx-auto">
          Upload PDF, TXT, or MD files to generate synthetic evaluation data. 
          Our AI will analyze your content and create sophisticated question-answer pairs.
        </p>
      </div>

      {/* Error Display */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <h3 className="text-red-700 font-medium">Upload Errors</h3>
          </div>
          <ul className="space-y-1">
            {errors.map((error, index) => (
              <li key={index} className="text-red-600 text-sm">• {error}</li>
            ))}
          </ul>
          <button
            onClick={() => setErrors([])}
            className="btn-clean mt-2 text-red-600 hover:text-red-800 text-sm underline"
            style={{
              backgroundColor: 'transparent !important',
              color: '#ef4444 !important',
              border: 'none !important',
              textDecoration: 'underline'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.color = '#dc2626 !important';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.color = '#ef4444 !important';
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
          isDragActive && !isDragReject
            ? 'border-primary-500 bg-primary-100/20 scale-105'
            : isDragReject
            ? 'border-red-400 bg-red-50'
            : 'border-light-400 hover:border-primary-400 hover:bg-primary-50/30'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <div className={`w-16 h-16 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
            isDragActive && !isDragReject 
              ? 'border-primary-500 bg-primary-100/30 scale-110' 
              : isDragReject
              ? 'border-red-400 bg-red-100/30'
              : 'border-light-400'
          }`}>
            {isDragReject ? (
              <AlertCircle className="w-8 h-8 text-red-500" />
            ) : (
              <Upload className={`w-8 h-8 ${
                isDragActive ? 'text-primary-600' : 'text-primary-600'
              }`} />
            )}
          </div>
          
          <div>
            <p className="text-lg font-medium text-primary-700 mb-2">
              {isDragReject 
                ? 'Some files are not supported' 
                : isDragActive 
                ? 'Drop files here' 
                : 'Drag & drop files here'
              }
            </p>
            <p className="text-primary-700 text-sm">
              or <span className="text-primary-600 hover:text-primary-500 transition-colors cursor-pointer">browse files</span>
            </p>
          </div>
          
          <div className="text-xs text-primary-600">
            Supports PDF, TXT, MD • Max 10MB per file • Up to 10 files
            {documents.length > 0 && (
              <span className="block mt-1">
                ({documents.length}/10 documents uploaded)
              </span>
            )}
          </div>
        </div>
        
        {isLoading && (
          <div className="absolute inset-0 bg-white/90 rounded-2xl flex items-center justify-center">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-primary-700">Processing files...</span>
            </div>
          </div>
        )}
      </div>

      {/* Text Input Area */}
      <div className="bg-white/80 rounded-2xl p-6 border border-light-300 shadow-light-lg">
        <h3 className="text-lg font-semibold text-primary-700 mb-4">Or paste text directly</h3>
        <div className="space-y-4">
          <div className="relative">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your document content here..."
              className="w-full h-32 bg-light-100/50 border border-light-300 rounded-xl px-4 py-3 text-primary-700 placeholder-primary-500 resize-none focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-colors"
              maxLength={50000}
            />
            <div className="absolute bottom-2 right-2 text-xs text-primary-500">
              {textInput.length}/50,000
            </div>
          </div>
          <div
            onClick={() => {
              if (textInput.trim() && documents.length < 10) {
                addTextDocument();
              }
            }}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && textInput.trim() && documents.length < 10) {
                e.preventDefault();
                addTextDocument();
              }
            }}
            style={{
              backgroundColor: (!textInput.trim() || documents.length >= 10) ? '#f1f5f9' : '#7c3aed',
              color: (!textInput.trim() || documents.length >= 10) ? '#9ca3af' : '#ffffff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: '500',
              fontSize: '14px',
              cursor: (!textInput.trim() || documents.length >= 10) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              outline: 'none',
              userSelect: 'none',
              display: 'inline-block'
            }}
            ref={(el) => {
              if (el) {
                el.style.setProperty('background-color', (!textInput.trim() || documents.length >= 10) ? '#f1f5f9' : '#7c3aed', 'important');
                el.style.setProperty('color', (!textInput.trim() || documents.length >= 10) ? '#9ca3af' : '#ffffff', 'important');
                el.style.setProperty('border', 'none', 'important');
              }
            }}
            onMouseEnter={(e) => {
              if (textInput.trim() && documents.length < 10) {
                e.currentTarget.style.setProperty('background-color', '#6d28d9', 'important');
                e.currentTarget.style.setProperty('color', '#ffffff', 'important');
              }
            }}
            onMouseLeave={(e) => {
              if (textInput.trim() && documents.length < 10) {
                e.currentTarget.style.setProperty('background-color', '#7c3aed', 'important');
                e.currentTarget.style.setProperty('color', '#ffffff', 'important');
              }
            }}
          >
            Add Text Document
          </div>
          {documents.length >= 10 && (
            <p className="text-xs text-red-600">Maximum of 10 documents reached</p>
          )}
        </div>
      </div>

      {/* Uploaded Documents List */}
      {documents.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-primary-700">
              Uploaded Documents ({documents.length}/10)
            </h3>
            <button
              onClick={clearAllDocuments}
              className="btn-clean text-sm text-primary-600 hover:text-red-600 transition-colors"
              style={{
                backgroundColor: 'transparent !important',
                color: '#7c3aed !important',
                border: 'none !important'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.color = '#ef4444 !important';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.color = '#7c3aed !important';
              }}
            >
              Clear All
            </button>
          </div>
          <div className="grid gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 bg-white/80 rounded-xl border border-light-300 shadow-light-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-primary-700">{doc.source}</h4>
                    <div className="flex items-center space-x-4 text-sm text-primary-600">
                      <span>{formatFileSize(doc.size || 0)}</span>
                      <span>•</span>
                      <span>{doc.content.length} characters</span>
                      {doc.type === 'application/pdf' && (
                        <>
                          <span>•</span>
                          <span className="text-amber-600">PDF (content extraction pending)</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-1 text-accent-emerald">
                    <CheckCircle className="w-4 h-4" />
                    <span className="text-sm font-medium">Ready</span>
                  </div>
                  <button
                    onClick={() => removeDocument(doc.id)}
                    className="btn-clean p-2 text-primary-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    style={{
                      backgroundColor: 'transparent !important',
                      color: '#7c3aed !important',
                      border: 'none !important',
                      padding: '8px',
                      borderRadius: '8px'
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.color = '#ef4444 !important';
                      e.currentTarget.style.backgroundColor = '#fef2f2 !important';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.color = '#7c3aed !important';
                      e.currentTarget.style.backgroundColor = 'transparent !important';
                    }}
                  >
                    <X className="w-4 h-4" style={{ color: 'inherit' }} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Button */}
      {documents.length > 0 && (
        <div className="flex justify-center pt-4">
          <button
            onClick={onNext}
            className="bg-primary-700 hover:bg-primary-600 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-200 hover:shadow-purple-glow flex items-center space-x-2"
            style={{
              backgroundColor: '#7c3aed !important',
              color: '#ffffff !important',
              border: 'none !important'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#6d28d9 !important';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#7c3aed !important';
            }}
          >
            <span style={{ color: '#ffffff !important' }}>Continue to Generation</span>
            <CheckCircle className="w-5 h-5" style={{ color: '#ffffff !important' }} />
          </button>
        </div>
      )}
    </div>
  );
} 