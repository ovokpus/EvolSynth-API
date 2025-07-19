"use client";

import { useState } from "react";
import { Download, Copy, BarChart3, FileText, MessageSquare, Lightbulb, RotateCcw, CheckCircle, Star, Clock, TrendingUp, Share } from "lucide-react";
import { GenerationResults, ResultsDisplayProps, DisplayQuestion, EnhancedContext } from "@/types";
import { getDisplayQuestions } from "@/services/api";
import MarkdownRenderer from "./MarkdownRenderer";

export default function ResultsDisplay({ results, onReset }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<'questions' | 'evaluation' | 'export' | 'insights'>('questions');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLevel, setSelectedLevel] = useState<string>("all");

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const exportData = (format: 'json' | 'csv' | 'txt') => {
    if (!results) return;
    
    let content = '';
    let filename = '';
    let mimeType = '';

    if (format === 'json') {
      content = JSON.stringify(results, null, 2);
      filename = `evolsynth-results-${Date.now()}.json`;
      mimeType = 'application/json';
    } else if (format === 'csv') {
      // Enhanced CSV format
      const headers = ['Question ID', 'Question', 'Answer', 'Context', 'Level', 'Confidence', 'Source'];
      const csvRows = [headers.join(',')];
      
      displayQuestions.forEach(q => {
        const row = [
          `"${q.id || 'N/A'}"`,
          `"${q.question.replace(/"/g, '""')}"`,
          `"${q.answer.replace(/"/g, '""')}"`,
          `"${Array.isArray(q.context) ? q.context.join('; ') : q.context || ''}"`,
          `"${q.level || 'unknown'}"`,
          `"${q.metadata?.confidence || 0}"`,
          `"${q.metadata?.source || 'unknown'}"`
        ];
        csvRows.push(row.join(','));
      });
      
      content = csvRows.join('\n');
      filename = `evolsynth-results-${Date.now()}.csv`;
      mimeType = 'text/csv';
    } else if (format === 'txt') {
      // Human-readable text format
      content = `EvolSynth Generation Results\n`;
      content += `Generated: ${new Date().toLocaleString()}\n`;
      content += `Total Questions: ${displayQuestions.length}\n`;
      content += `Processing Time: ${results.processingTime?.toFixed(1)}s\n\n`;
      
      content += `=== QUESTIONS & ANSWERS ===\n\n`;
      displayQuestions.forEach((q, index) => {
        content += `${index + 1}. ${q.question}\n`;
        content += `Answer: ${q.answer}\n`;
        content += `Level: ${q.level}\n`;
        if (q.context) {
          content += `Context: ${Array.isArray(q.context) ? q.context.join(', ') : q.context}\n`;
        }
        content += `\n`;
      });
      
      filename = `evolsynth-results-${Date.now()}.txt`;
      mimeType = 'text/plain';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Calculate overall quality score from individual metrics
  const calculateOverallQuality = () => {
    if (!results?.evaluation?.overall_scores) return 0;
    const scores = Object.values(results.evaluation.overall_scores);
    return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
  };

  const shareResults = () => {
    const shareData = {
      title: 'EvolSynth Generation Results',
      text: `Generated ${displayQuestions.length} questions using EvolSynth AI`,
      url: window.location.href
    };

    if (navigator.share) {
      navigator.share(shareData);
    } else {
      const qualityScore = Math.round(calculateOverallQuality() * 100);
      copyToClipboard(
        `EvolSynth Results: Generated ${displayQuestions.length} questions with ${qualityScore}% quality score`,
        'share'
      );
    }
  };

  // Convert backend data to display format
  const displayQuestions: DisplayQuestion[] = results ? getDisplayQuestions(results) : [];
  
  const tabs = [
    { id: 'questions' as const, label: 'Questions & Answers', icon: MessageSquare, count: displayQuestions.length },
    { id: 'evaluation' as const, label: 'Quality Metrics', icon: BarChart3 },
    { id: 'insights' as const, label: 'Insights', icon: TrendingUp },
    { id: 'export' as const, label: 'Export Data', icon: Download },
  ];

  // Filter questions based on search and level
  const filteredQuestions = displayQuestions.filter(q => {
    const matchesSearch = searchTerm === "" || 
      q.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      q.answer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLevel = selectedLevel === "all" || q.level === selectedLevel;
    return matchesSearch && matchesLevel;
  });

  const questionsByLevel = displayQuestions.reduce((acc, q) => {
    const level = q.level || 'unknown';
    acc[level] = (acc[level] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (!results) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-light-200 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-light-500" />
        </div>
        <h3 className="text-lg font-semibold text-primary-800 mb-2">No Results Available</h3>
        <p className="text-light-600">Generate some synthetic data to see results here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Share */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <CheckCircle className="w-6 h-6 text-accent-emerald" />
          <h2 className="text-2xl font-bold text-primary-800">Generation Complete!</h2>
          <button
            onClick={shareResults}
            className="btn-clean ml-4 p-2 text-primary-600 hover:text-primary-500 transition-colors"
            title="Share results"
          >
            <Share className="w-5 h-5" />
          </button>
        </div>
        <p className="text-primary-700 max-w-2xl mx-auto">
          Your synthetic evaluation data has been successfully generated. 
          Review the questions, check quality metrics, and export your dataset.
        </p>
      </div>

      {/* Enhanced Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white/80 rounded-xl p-4 border border-light-300 text-center shadow-light-lg">
          <div className="text-2xl font-bold text-primary-700">{results.evolved_questions?.length || 0}</div>
          <div className="text-sm text-primary-600">Questions Generated</div>
          <div className="text-xs text-light-500 mt-1">
            {Object.entries(questionsByLevel).map(([level, count]) => `${level}: ${count}`).join(', ')}
          </div>
        </div>
        <div className="bg-white/80 rounded-xl p-4 border border-light-300 text-center shadow-light-lg">
          <div className="text-2xl font-bold text-primary-700">{results.documentsProcessed || 0}</div>
          <div className="text-sm text-primary-600">Documents Processed</div>
          <div className="text-xs text-light-500 mt-1">Input sources analyzed</div>
        </div>
        <div className="bg-white/80 rounded-xl p-4 border border-light-300 text-center shadow-light-lg">
          <div className="text-2xl font-bold text-primary-700">{Math.round(calculateOverallQuality() * 100)}%</div>
          <div className="text-sm text-primary-600">Quality Score</div>
          <div className="text-xs text-light-500 mt-1">AI-evaluated quality</div>
        </div>
        <div className="bg-white/80 rounded-xl p-4 border border-light-300 text-center shadow-light-lg">
          <div className="text-2xl font-bold text-primary-700">{results.processingTime?.toFixed(1) || 'N/A'}s</div>
          <div className="text-sm text-primary-600">Processing Time</div>
          <div className="text-xs text-light-500 mt-1">Generation duration</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-light-300">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <div
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setActiveTab(tab.id);
                }
              }}
              className={`flex items-center space-x-2 py-3 border-b-2 font-medium transition-colors cursor-pointer ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-700'
                  : 'border-transparent text-primary-600 hover:text-primary-700 hover:border-light-400'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count && (
                <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </div>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white/80 rounded-2xl border border-light-300 shadow-light-lg">
        {activeTab === 'questions' && (
          <div className="p-6">
            {/* Search and Filter */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search questions and answers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-light-100/50 border border-light-300 rounded-lg px-4 py-2 text-primary-700 placeholder-primary-500 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                />
              </div>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="bg-light-100/50 border border-light-300 rounded-lg px-4 py-2 text-primary-700 focus:outline-none focus:border-primary-500"
              >
                <option value="all">All Levels</option>
                <option value="simple">Simple</option>
                <option value="multi-context">Multi-Context</option>
                <option value="reasoning">Reasoning</option>
                <option value="complex">Complex</option>
              </select>
            </div>

            <h3 className="text-lg font-semibold text-primary-700 mb-4">
              Generated Questions & Answers ({filteredQuestions.length})
            </h3>
            
            {filteredQuestions.length > 0 ? (
              <div className="space-y-6">
                {filteredQuestions.map((qa, index) => (
                  <div key={`question-${qa.id}-${index}`} className="border border-light-300 rounded-xl p-6 bg-light-50/50">
                    {/* Question Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 text-sm font-medium">
                          {filteredQuestions.indexOf(qa) + 1}
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          qa.level === 'simple' 
                            ? 'bg-accent-emerald/20 text-accent-emerald' 
                            : qa.level === 'multi-context'
                            ? 'bg-accent-violet/20 text-accent-violet'
                            : 'bg-primary-100 text-primary-700'
                        }`}>
                          {qa.level || 'Unknown'} Level
                        </span>
                        {qa.metadata?.confidence && (
                          <div className="flex items-center space-x-1">
                            <Star className="w-3 h-3 text-amber-500" />
                            <span className="text-xs text-primary-600">
                              {Math.round(qa.metadata.confidence * 100)}%
                            </span>
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => copyToClipboard(
                          `Q: ${qa.question}\nA: ${qa.answer}${qa.context ? `\nContext: ${Array.isArray(qa.context) ? qa.context.join(', ') : qa.context}` : ''}`,
                          `qa-${qa.id}-${index}`
                        )}
                        className="text-primary-500 hover:text-primary-600 transition-colors"
                      >
                        {copiedId === `qa-${qa.id}-${index}` ? (
                          <CheckCircle className="w-4 h-4 text-accent-emerald" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>

                    {/* Question */}
                    <div className="mb-4">
                      <h4 className="font-medium text-primary-700 mb-2 flex items-center space-x-2">
                        <MessageSquare className="w-4 h-4" />
                        <span>Question</span>
                      </h4>
                      <div className="bg-white/60 p-4 rounded-lg border border-light-200 shadow-sm">
                        <MarkdownRenderer content={qa.question} contentType="question" enhanceFormatting={true} />
                      </div>
                    </div>

                    {/* Answer */}
                    <div className="mb-4">
                      <h4 className="font-medium text-primary-700 mb-2 flex items-center space-x-2">
                        <Lightbulb className="w-4 h-4" />
                        <span>Answer</span>
                      </h4>
                      <div className="bg-white/60 p-4 rounded-lg border border-light-200 shadow-sm">
                        <MarkdownRenderer content={qa.answer} contentType="answer" enhanceFormatting={true} />
                      </div>
                    </div>

                    {/* Context Summary */}
                    {qa.context && (
                      <div>
                        <h4 className="font-medium text-primary-700 mb-2 flex items-center space-x-2">
                          <FileText className="w-4 h-4" />
                          <span>Context Summary</span>
                          <span className="text-xs text-primary-500 bg-primary-100 px-2 py-0.5 rounded-full">AI Summarized</span>
                        </h4>
                        {Array.isArray(qa.context) ? (
                          <ul className="space-y-2">
                            {qa.context.map((ctx, i) => {
                              // Handle both string and enhanced context formats
                              const isEnhancedContext = typeof ctx === 'object' && ctx !== null && 'text' in ctx;
                              const contextText = isEnhancedContext ? (ctx as EnhancedContext).text : (ctx as string);
                              const contextSource = isEnhancedContext ? (ctx as EnhancedContext).source : null;
                              
                              return (
                                <li key={`context-${qa.id}-${index}-${i}`} className="bg-primary-50/50 p-3 rounded-lg border border-primary-200/60 shadow-sm">
                                  <div className="flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-primary-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                    <div className="flex-1">
                                      {contextSource && (
                                        <div className="flex items-center space-x-1 mb-1">
                                          <span className="text-xs text-primary-500 bg-primary-200/50 px-2 py-0.5 rounded-full font-medium">
                                            📄 {contextSource}
                                          </span>
                                        </div>
                                      )}
                                      <div className="text-xs text-primary-600 leading-relaxed">
                                        <MarkdownRenderer 
                                          content={contextText} 
                                          contentType="general"
                                          enhanceFormatting={true}
                                          className="text-xs [&_p]:text-xs [&_p]:mb-1 [&_li]:text-xs [&_strong]:text-xs"
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </li>
                              );
                            })}
                          </ul>
                        ) : (
                          <div className="bg-primary-50/50 p-3 rounded-lg border border-primary-200/60 shadow-sm">
                            <div className="text-xs text-primary-600 leading-relaxed">
                              <MarkdownRenderer 
                                content={qa.context as string} 
                                contentType="general"
                                enhanceFormatting={true}
                                className="text-xs [&_p]:text-xs [&_p]:mb-1 [&_li]:text-xs [&_strong]:text-xs"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="w-12 h-12 text-light-400 mx-auto mb-4" />
                <p className="text-primary-600">No questions match your search criteria.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'evaluation' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">Quality Assessment</h3>
            
            {results.evaluation ? (
              <div className="space-y-6">
                {/* Overall Score */}
                <div className="text-center p-6 bg-primary-50/50 rounded-xl border border-primary-200">
                  <div className="text-4xl font-bold text-primary-700 mb-2">
                    {Math.round(calculateOverallQuality() * 100)}%
                  </div>
                  <div className="text-primary-600 font-medium">Overall Quality Score</div>
                </div>

                {/* Detailed Metrics */}
                {results.evaluation.overall_scores && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(results.evaluation.overall_scores).map(([key, value]) => (
                      <div key={key} className="bg-white/60 p-4 rounded-xl border border-light-200">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-medium text-primary-700 capitalize">{key}</span>
                          <span className="text-primary-700 font-bold">{Math.round((value as number) * 100)}%</span>
                        </div>
                        <div className="w-full bg-light-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-primary-500 to-primary-400 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(value as number) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="w-12 h-12 text-light-400 mx-auto mb-4" />
                <p className="text-primary-600">No evaluation data available.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">Generation Insights</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Question Distribution */}
              <div className="bg-white/60 p-4 rounded-xl border border-light-200">
                <h4 className="font-medium text-primary-700 mb-3">Question Distribution</h4>
                <div className="space-y-2">
                  {Object.entries(questionsByLevel).map(([level, count]) => (
                    <div key={level} className="flex justify-between items-center">
                      <span className="text-primary-600 capitalize">{level}</span>
                      <span className="text-primary-700 font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Processing Stats */}
              <div className="bg-white/60 p-4 rounded-xl border border-light-200">
                <h4 className="font-medium text-primary-700 mb-3">Processing Statistics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-primary-600">Processing Time</span>
                    <span className="text-primary-700 font-medium">{results.processingTime?.toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-primary-600">Questions/Second</span>
                    <span className="text-primary-700 font-medium">
                      {((results.evolved_questions?.length || 0) / (results.processingTime || 1)).toFixed(1)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-primary-600">Generation Mode</span>
                    <span className="text-primary-700 font-medium">
                      {results.settings?.concurrentProcessing ? 'Concurrent' : 'Sequential'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Settings Used */}
            {results.settings && (
              <div className="mt-6 bg-blue-50 p-4 rounded-xl border border-blue-200">
                <h4 className="font-medium text-blue-700 mb-3">Generation Settings Used</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-blue-600">Evolution Levels:</span>
                    <span className="text-blue-700 font-medium ml-1">{results.settings.evolutionLevels}</span>
                  </div>
                  <div>
                    <span className="text-blue-600">Questions/Level:</span>
                    <span className="text-blue-700 font-medium ml-1">{results.settings.questionsPerLevel}</span>
                  </div>
                  <div>
                    <span className="text-blue-600">Temperature:</span>
                    <span className="text-blue-700 font-medium ml-1">{results.settings.temperature}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'export' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">Export Your Dataset</h3>
            
            <div className="space-y-6">
              <p className="text-primary-600">
                Download your generated synthetic evaluation data in your preferred format.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => exportData('json')}
                  className="flex flex-col items-center justify-center space-y-3 p-6 bg-white/60 border border-light-300 rounded-xl hover:border-primary-300 hover:bg-primary-50/30 transition-all duration-200"
                >
                  <FileText className="w-8 h-8 text-primary-600" />
                  <div className="text-center">
                    <div className="font-medium text-primary-700">JSON Format</div>
                    <div className="text-sm text-primary-600">Complete dataset with metadata</div>
                  </div>
                </button>
                
                <button
                  onClick={() => exportData('csv')}
                  className="flex flex-col items-center justify-center space-y-3 p-6 bg-white/60 border border-light-300 rounded-xl hover:border-primary-300 hover:bg-primary-50/30 transition-all duration-200"
                >
                  <Download className="w-8 h-8 text-primary-600" />
                  <div className="text-center">
                    <div className="font-medium text-primary-700">CSV Format</div>
                    <div className="text-sm text-primary-600">Spreadsheet-compatible format</div>
                  </div>
                </button>

                <button
                  onClick={() => exportData('txt')}
                  className="flex flex-col items-center justify-center space-y-3 p-6 bg-white/60 border border-light-300 rounded-xl hover:border-primary-300 hover:bg-primary-50/30 transition-all duration-200"
                >
                  <FileText className="w-8 h-8 text-primary-600" />
                  <div className="text-center">
                    <div className="font-medium text-primary-700">Text Format</div>
                    <div className="text-sm text-primary-600">Human-readable format</div>
                  </div>
                </button>
              </div>

              {/* Export Statistics */}
              <div className="bg-light-100/50 p-4 rounded-lg border border-light-200">
                <h4 className="font-medium text-primary-700 mb-2">Export Statistics</h4>
                <div className="text-sm text-primary-600 space-y-1">
                  <div>Total Questions: {results.evolved_questions?.length || 0}</div>
                  <div>Estimated File Sizes:</div>
                  <div className="ml-4">
                    <div>• JSON: ~{Math.round((JSON.stringify(results).length / 1024) * 1.2)}KB</div>
                    <div>• CSV: ~{Math.round((results.evolved_questions?.length || 0) * 0.5)}KB</div>
                    <div>• TXT: ~{Math.round((results.evolved_questions?.length || 0) * 1.0)}KB</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Reset Button */}
      <div className="flex justify-center pt-8 pb-8 mt-8">
        <button
          onClick={onReset}
          style={{ 
            backgroundColor: '#7c3aed !important',
            color: '#ffffff !important',
            border: 'none !important',
            minHeight: '60px',
            fontSize: '18px',
            padding: '16px 32px',
            borderRadius: '12px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            transition: 'all 0.2s',
            cursor: 'pointer'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#6d28d9 !important';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#7c3aed !important';
          }}
        >
          <RotateCcw className="w-5 h-5" style={{ color: '#ffffff !important' }} />
          <span style={{ color: '#ffffff !important' }}>Generate New Dataset</span>
        </button>
      </div>
    </div>
  );
} 