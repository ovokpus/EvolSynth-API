"use client";

import { useState, useEffect } from "react";
import { Zap, Settings, Brain, Clock, CheckCircle, AlertTriangle, Info, Calculator } from "lucide-react";
import { UploadedDocument, GenerationResults, GenerationInterfaceProps, FrontendGenerationSettings } from "@/types";
import { generateSyntheticData } from "@/services/api";

export default function GenerationInterface({ documents, onComplete, onBack }: GenerationInterfaceProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [settings, setSettings] = useState<FrontendGenerationSettings>({
    evolutionLevels: 3,
    questionsPerLevel: 5,
    maxQuestions: 50,
    simpleEvolutionCount: 3,
    multiContextEvolutionCount: 3,
    reasoningEvolutionCount: 2,
    complexEvolutionCount: 1,
    includeContextual: true,
    includeReasoning: true,
    evaluationEnabled: true,
    temperature: 0.7,
    concurrentProcessing: true,
    fastMode: true,
    outputFormat: 'json' as 'json' | 'csv' | 'both',
  });

  // Calculate estimated metrics
  const estimatedQuestions = Math.min(
    settings.simpleEvolutionCount + settings.multiContextEvolutionCount + settings.reasoningEvolutionCount + settings.complexEvolutionCount,
    settings.maxQuestions
  );
  
  const estimatedTime = settings.fastMode 
    ? Math.ceil(estimatedQuestions * 0.1) // Ultra-fast: 0.1 seconds per question with single API call
    : settings.concurrentProcessing 
      ? Math.ceil(estimatedQuestions * 0.3) // 0.3 seconds per question with concurrency
      : Math.ceil(estimatedQuestions * 1.2); // 1.2 seconds per question without concurrency

  const totalCharacters = documents.reduce((sum, doc) => sum + doc.content.length, 0);

  // Validation
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  useEffect(() => {
    const errors: string[] = [];
    
    if (settings.questionsPerLevel < 1 || settings.questionsPerLevel > 20) {
      errors.push("Questions per level must be between 1 and 20");
    }
    
    if (settings.maxQuestions < 5 || settings.maxQuestions > 200) {
      errors.push("Maximum questions must be between 5 and 200");
    }
    
    if (settings.temperature < 0.1 || settings.temperature > 1.0) {
      errors.push("Temperature must be between 0.1 and 1.0");
    }
    
    if (settings.simpleEvolutionCount < 0 || settings.simpleEvolutionCount > 20) {
      errors.push("Simple evolution count must be between 0 and 20");
    }
    
    if (settings.multiContextEvolutionCount < 0 || settings.multiContextEvolutionCount > 20) {
      errors.push("Multi-context evolution count must be between 0 and 20");
    }
    
    if (settings.reasoningEvolutionCount < 0 || settings.reasoningEvolutionCount > 20) {
      errors.push("Reasoning evolution count must be between 0 and 20");
    }
    
    if (settings.complexEvolutionCount < 0 || settings.complexEvolutionCount > 20) {
      errors.push("Complex evolution count must be between 0 and 20");
    }
    
    if (estimatedQuestions === 0) {
      errors.push("At least one evolution type must have a count greater than 0");
    }
    
    if (estimatedQuestions > settings.maxQuestions) {
      errors.push(`Estimated questions (${estimatedQuestions}) exceeds maximum limit (${settings.maxQuestions})`);
    }

    if (totalCharacters > 10000000) {
      errors.push("Total document content exceeds 10,000,000 characters. Consider reducing document size.");
    }
    
    // Debug logging
    if (errors.length > 0) {
      console.log('🚨 Validation Errors:', errors);
      console.log('📊 Debug Info:', {
        estimatedQuestions,
        totalCharacters,
        documentsCount: documents.length,
        evolutionCounts: {
          simple: settings.simpleEvolutionCount,
          multiContext: settings.multiContextEvolutionCount,
          reasoning: settings.reasoningEvolutionCount,
          complex: settings.complexEvolutionCount
        }
      });
    }
    
    setValidationErrors(errors);
  }, [settings, estimatedQuestions, totalCharacters]);

  // Real generation process using FastAPI backend with realistic progress tracking
  const performRealGeneration = async () => {
    try {
      setCurrentStep("Connecting to backend...");
      setProgress(5);
      await new Promise(resolve => setTimeout(resolve, 300));

      setCurrentStep("Processing documents...");
      setProgress(15);
      await new Promise(resolve => setTimeout(resolve, 400));

      setCurrentStep("Initializing generation models...");
      setProgress(25);
      await new Promise(resolve => setTimeout(resolve, 500));

      setCurrentStep("Generating questions...");
      setProgress(40);
      
      // Start the actual API call
      const results = await generateSyntheticData(documents, settings);
      
      setCurrentStep("Evaluating quality...");
      setProgress(75);
      await new Promise(resolve => setTimeout(resolve, 400));
      
      setCurrentStep("Finalizing results...");
      setProgress(90);
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setCurrentStep("Generation complete!");
      setProgress(100);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      onComplete(results);
      
    } catch (error) {
      setCurrentStep(`Error: ${error instanceof Error ? error.message : 'Generation failed'}`);
      setProgress(0);
      
      // Show error for a few seconds then allow retry
      setTimeout(() => {
        setIsGenerating(false);
      }, 3000);
    }
  };

  const startGeneration = () => {
    if (validationErrors.length > 0) {
      return; // Don't start if there are validation errors
    }
    
    setIsGenerating(true);
    setProgress(0);
    performRealGeneration();
  };

  const resetSettings = () => {
    setSettings({
      evolutionLevels: 3,
      questionsPerLevel: 5,
      maxQuestions: 50,
      simpleEvolutionCount: 3,
      multiContextEvolutionCount: 3,
      reasoningEvolutionCount: 2,
      complexEvolutionCount: 1,
      includeContextual: true,
      includeReasoning: true,
      evaluationEnabled: true,
      temperature: 0.7,
      concurrentProcessing: true,
      fastMode: true,
      outputFormat: 'json' as 'json' | 'csv' | 'both',
    });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-primary-700 mb-2">Configure Generation Settings</h2>
        <p className="text-primary-700 max-w-2xl mx-auto">
          Customize how your synthetic evaluation data will be generated using our advanced Evol-Instruct methodology.
        </p>
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <h3 className="text-red-700 font-medium">Configuration Issues</h3>
          </div>
          <ul className="space-y-1">
            {validationErrors.map((error, index) => (
              <li key={index} className="text-red-600 text-sm">• {error}</li>
            ))}
          </ul>
        </div>
      )}

      {!isGenerating ? (
        <>
          {/* Settings Panel */}
          <div className="bg-white/80 rounded-2xl p-6 border border-light-300 shadow-light-lg">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-primary-700">Generation Parameters</h3>
              </div>
              <button
                onClick={resetSettings}
                className="text-sm text-primary-600 hover:text-primary-500 transition-colors"
              >
                Reset to Defaults
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Evolution Levels */}
              <div>
                <label className="block text-sm font-medium text-primary-700 mb-2">
                  Evolution Levels
                </label>
                <select
                  value={settings.evolutionLevels}
                  onChange={(e) => setSettings({...settings, evolutionLevels: Number(e.target.value)})}
                  className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                >
                  <option value={2}>2 Levels (Simple → Multi-Context)</option>
                  <option value={3}>3 Levels (Simple → Multi-Context → Reasoning)</option>
                  <option value={4}>4 Levels (Full Evolution Chain)</option>
                </select>
                <p className="text-xs text-primary-600 mt-1">Higher levels create more sophisticated questions</p>
              </div>

              {/* Questions Per Level */}
              <div>
                <label className="block text-sm font-medium text-primary-700 mb-2">
                  Questions Per Level
                </label>
                <input
                  type="number"
                  min={1}
                  max={20}
                  value={settings.questionsPerLevel}
                  onChange={(e) => setSettings({...settings, questionsPerLevel: Number(e.target.value)})}
                  className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                />
                <p className="text-xs text-primary-600 mt-1">Number of questions to generate per evolution level</p>
              </div>

              {/* Max Questions */}
              <div>
                <label className="block text-sm font-medium text-primary-700 mb-2">
                  Maximum Total Questions
                </label>
                <input
                  type="number"
                  min={5}
                  max={200}
                  value={settings.maxQuestions}
                  onChange={(e) => setSettings({...settings, maxQuestions: Number(e.target.value)})}
                  className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                />
                <p className="text-xs text-primary-600 mt-1">Maximum questions to generate across all levels</p>
              </div>
            </div>

            {/* Evolution Type Counts */}
            <div className="mt-6">
              <h4 className="text-sm font-medium text-primary-700 mb-3">Evolution Type Distribution</h4>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Simple Evolution */}
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-2">
                    Simple Evolution
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={20}
                    value={settings.simpleEvolutionCount}
                    onChange={(e) => setSettings({...settings, simpleEvolutionCount: Number(e.target.value)})}
                    className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                  <p className="text-xs text-primary-600 mt-1">Clear, direct questions</p>
                </div>

                {/* Multi-Context Evolution */}
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-2">
                    Multi-Context
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={20}
                    value={settings.multiContextEvolutionCount}
                    onChange={(e) => setSettings({...settings, multiContextEvolutionCount: Number(e.target.value)})}
                    className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                  <p className="text-xs text-primary-600 mt-1">Cross-document analysis</p>
                </div>

                {/* Reasoning Evolution */}
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-2">
                    Reasoning
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={20}
                    value={settings.reasoningEvolutionCount}
                    onChange={(e) => setSettings({...settings, reasoningEvolutionCount: Number(e.target.value)})}
                    className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                  <p className="text-xs text-primary-600 mt-1">Multi-step thinking</p>
                </div>

                {/* Complex Evolution */}
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-2">
                    Complex
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={20}
                    value={settings.complexEvolutionCount}
                    onChange={(e) => setSettings({...settings, complexEvolutionCount: Number(e.target.value)})}
                    className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                  <p className="text-xs text-primary-600 mt-1">Meta-cognitive synthesis</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Temperature */}
              <div>
                <label className="block text-sm font-medium text-primary-700 mb-2">
                  Temperature: {settings.temperature}
                </label>
                <input
                  type="range"
                  min={0.1}
                  max={1.0}
                  step={0.1}
                  value={settings.temperature}
                  onChange={(e) => setSettings({...settings, temperature: Number(e.target.value)})}
                  className="w-full h-2 bg-light-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-primary-600 mt-1">
                  <span>Conservative (0.1)</span>
                  <span>Creative (1.0)</span>
                </div>
              </div>
            </div>

            {/* Advanced Options */}
            <div className="mt-6 space-y-4">
              <h4 className="text-sm font-medium text-primary-700 mb-3">Advanced Options</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.includeContextual}
                    onChange={(e) => setSettings({...settings, includeContextual: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-light-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-primary-700">Multi-Context Questions</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.includeReasoning}
                    onChange={(e) => setSettings({...settings, includeReasoning: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-light-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-primary-700">Reasoning Questions</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.evaluationEnabled}
                    onChange={(e) => setSettings({...settings, evaluationEnabled: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-light-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-primary-700">LLM-as-judge Evaluation</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.concurrentProcessing}
                    onChange={(e) => setSettings({...settings, concurrentProcessing: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-light-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-primary-700">Concurrent Processing</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.fastMode}
                    onChange={(e) => setSettings({...settings, fastMode: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-light-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-primary-700 flex items-center">
                    <Zap className="w-4 h-4 mr-1 text-accent-emerald" />
                    Ultra-Fast Mode
                  </span>
                </label>
              </div>

              {/* Output Format */}
              <div>
                <label className="block text-sm font-medium text-primary-700 mb-2">
                  Output Format
                </label>
                <select
                  value={settings.outputFormat}
                  onChange={(e) => setSettings({...settings, outputFormat: e.target.value as 'json' | 'csv' | 'both'})}
                  className="w-full bg-light-100/50 border border-light-300 rounded-lg px-3 py-2 text-primary-700 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                >
                  <option value="json">JSON Format</option>
                  <option value="csv">CSV Format</option>
                  <option value="both">Both JSON & CSV</option>
                </select>
              </div>
            </div>
          </div>

          {/* Preview Panel */}
          <div className="bg-primary-50/50 rounded-2xl p-6 border border-primary-200">
            <div className="flex items-center space-x-2 mb-4">
              <Calculator className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold text-primary-700">Generation Preview</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white/60 p-4 rounded-xl border border-primary-200">
                <div className="text-2xl font-bold text-primary-700">{estimatedQuestions}</div>
                <div className="text-sm text-primary-600">Estimated Questions</div>
              </div>
              
              <div className="bg-white/60 p-4 rounded-xl border border-primary-200">
                <div className="text-2xl font-bold text-primary-700">{documents.length}</div>
                <div className="text-sm text-primary-600">Input Documents</div>
              </div>
              
              <div className="bg-white/60 p-4 rounded-xl border border-primary-200">
                <div className="text-2xl font-bold text-primary-700">~{estimatedTime}s</div>
                <div className="text-sm text-primary-600">
                  Processing Time {settings.fastMode ? <span className="text-accent-emerald font-semibold">⚡ Ultra-Fast</span> : settings.concurrentProcessing && <span className="text-accent-emerald">(Concurrent)</span>}
                </div>
              </div>
              
              <div className="bg-white/60 p-4 rounded-xl border border-primary-200">
                <div className="text-2xl font-bold text-primary-700">{(totalCharacters / 1000).toFixed(1)}K</div>
                <div className="text-sm text-primary-600">Characters</div>
              </div>
            </div>

            {/* Info Box */}
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <Info className="w-4 h-4 text-blue-500 mt-0.5" />
                <div className="text-sm text-blue-700">
                  <strong>Generation Process:</strong> Your documents will be processed through {settings.evolutionLevels} evolution levels, 
                  creating {estimatedQuestions} questions total. {settings.fastMode ? '⚡ Ultra-fast mode uses a single optimized API call for maximum speed.' : settings.concurrentProcessing ? 'Concurrent processing enabled for faster generation.' : 'Sequential processing selected.'}
                </div>
              </div>
            </div>
          </div>

          {/* Document Summary */}
          <div className="bg-white/60 rounded-2xl p-6 border border-light-300 shadow-light-lg">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">Documents to Process</h3>
            <div className="grid gap-3">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-light-100/50 rounded-lg border border-light-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Brain className="w-4 h-4 text-primary-600" />
                    </div>
                    <div>
                      <div className="font-medium text-primary-700">{doc.source}</div>
                      <div className="text-sm text-primary-600">
                        {doc.content.length.toLocaleString()} characters
                        {doc.type === 'application/pdf' && (
                          <span className="ml-2 text-amber-600">• PDF</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <CheckCircle className="w-5 h-5 text-accent-emerald" />
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <button
              onClick={onBack}
              className="bg-light-200 hover:bg-light-300 text-primary-700 px-6 py-3 rounded-xl font-medium transition-all duration-200"
            >
              Back to Upload
            </button>
            <button
              onClick={startGeneration}
              disabled={validationErrors.length > 0}
              className="bg-primary-700 hover:bg-primary-600 disabled:bg-light-300 disabled:text-light-500 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-200 hover:shadow-purple-glow flex items-center space-x-2 disabled:cursor-not-allowed"
            >
              <Zap className="w-5 h-5 text-white" />
              <span className="text-white">Start Generation</span>
            </button>
          </div>
        </>
      ) : (
        /* Generation Progress */
        <div className="bg-white/80 rounded-2xl p-8 border border-light-300 shadow-light-lg text-center">
          <div className="mb-6">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Brain className="w-10 h-10 text-primary-600 animate-pulse" />
            </div>
            <h3 className="text-xl font-semibold text-primary-700 mb-2">Generating Synthetic Data</h3>
            <p className="text-primary-700">Using advanced Evol-Instruct methodology with LangGraph workflows</p>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="w-full bg-light-200 rounded-full h-4 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm text-primary-600 mt-2">
              <span>{Math.round(progress)}% complete</span>
              <span>~{Math.max(0, Math.round((100 - progress) * estimatedTime / 100))}s remaining</span>
            </div>
          </div>

          {/* Current Step */}
          <div className="flex items-center justify-center space-x-3 text-primary-700 mb-6">
            <Clock className="w-5 h-5 animate-spin" />
            <span className="font-medium">{currentStep}</span>
          </div>

          {/* Progress Steps */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            {[
              "Document Analysis",
              "Base Questions",
              "Question Evolution", 
              "Quality Evaluation",
              "Results Compilation",
              "Final Processing"
            ].map((step, index) => (
              <div
                key={step}
                className={`p-3 rounded-lg border ${
                  progress > (index * 16.67)
                    ? 'bg-primary-50 border-primary-200 text-primary-700'
                    : 'bg-light-100 border-light-300 text-primary-600'
                }`}
              >
                <div className="flex items-center space-x-2">
                  {progress > ((index + 1) * 16.67) ? (
                    <CheckCircle className="w-4 h-4 text-accent-emerald" />
                  ) : progress > (index * 16.67) ? (
                    <Clock className="w-4 h-4 animate-spin" />
                  ) : (
                    <div className="w-4 h-4 border-2 border-primary-400 rounded-full" />
                  )}
                  <span className="font-medium text-xs">{step}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 