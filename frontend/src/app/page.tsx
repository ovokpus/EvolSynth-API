"use client";

import { useState } from "react";
import { Brain, Zap, Shield, BarChart3, Upload, Play, Download, CheckCircle } from "lucide-react";
import Navigation from "@/components/Navigation";
import HeroSection from "@/components/HeroSection";
import DocumentUpload from "@/components/DocumentUpload";
import GenerationInterface from "@/components/GenerationInterface";
import ResultsDisplay from "@/components/ResultsDisplay";
import { DocumentInput, GenerationResults, GenerationStep } from "@/types";

export default function Home() {
  const [currentStep, setCurrentStep] = useState<GenerationStep>('upload');
  const [documents, setDocuments] = useState<DocumentInput[]>([]);
  const [generationResults, setGenerationResults] = useState<GenerationResults | null>(null);

  const features = [
    {
      icon: Brain,
      title: "Smart Evolution",
      description: "Three-tier question evolution: Simple → Multi-Context → Reasoning",
      gradient: "from-accent-purple to-accent-violet",
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Concurrent processing with LangGraph workflows - 3x faster generation",
      gradient: "from-accent-violet to-accent-fuchsia",
    },
    {
      icon: Shield,
      title: "Quality Assured",
      description: "Built-in LLM-as-judge evaluation for comprehensive quality control",
      gradient: "from-accent-fuchsia to-accent-pink",
    },
    {
      icon: BarChart3,
      title: "Real-time Analytics",
      description: "Live progress tracking and detailed performance metrics",
      gradient: "from-accent-pink to-accent-emerald",
    },
  ];

  const steps = [
    { id: 'upload' as const, title: 'Upload Documents', icon: Upload },
    { id: 'generate' as const, title: 'Generate Data', icon: Play },
    { id: 'results' as const, title: 'View Results', icon: Download },
  ];

  return (
    <main className="min-h-screen">
      <Navigation />
      
      {/* Hero Section */}
      <HeroSection />

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-primary-700 mb-4">
              Powered by Advanced AI
            </h2>
            <p className="text-primary-700 text-lg max-w-3xl mx-auto">
              Revolutionary Evol-Instruct methodology with LangGraph workflows for unparalleled synthetic data quality
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group relative p-6 rounded-2xl bg-white/70 backdrop-blur-sm border border-light-300 hover:border-primary-300 transition-all duration-300 hover:shadow-purple-glow animate-slide-up shadow-light-lg"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.gradient} p-3 mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-primary-700 mb-2">{feature.title}</h3>
                <p className="text-primary-700 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Main Interface */}
      <section id="interface" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Step Indicator */}
          <div className="flex justify-center mb-12">
            <div className="flex space-x-8">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div
                    className={`flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 ${
                      currentStep === step.id
                        ? 'bg-primary-600 border-primary-500 text-white shadow-purple-glow'
                        : currentStep === 'generate' && step.id === 'upload'
                        ? 'bg-accent-emerald border-accent-emerald text-white'
                        : currentStep === 'results' && (step.id === 'upload' || step.id === 'generate')
                        ? 'bg-accent-emerald border-accent-emerald text-white'
                        : 'border-light-400 text-primary-700'
                    }`}
                  >
                    {(currentStep === 'generate' && step.id === 'upload') ||
                     (currentStep === 'results' && (step.id === 'upload' || step.id === 'generate')) ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : (
                      <step.icon className="w-6 h-6" />
                    )}
                  </div>
                  <span
                    className={`ml-3 font-medium ${
                      currentStep === step.id ? 'text-primary-700' : 'text-primary-600'
                    }`}
                  >
                    {step.title}
                  </span>
                  {index < steps.length - 1 && (
                    <div className="w-16 h-0.5 bg-light-300 ml-6"></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 border border-light-300 shadow-light-lg">
            {currentStep === 'upload' && (
              <DocumentUpload
                documents={documents}
                setDocuments={setDocuments}
                onNext={() => setCurrentStep('generate')}
              />
            )}
            
            {currentStep === 'generate' && (
              <GenerationInterface
                documents={documents}
                onComplete={(results: GenerationResults) => {
                  setGenerationResults(results);
                  setCurrentStep('results');
                }}
                onBack={() => setCurrentStep('upload')}
              />
            )}
            
            {currentStep === 'results' && (
              <ResultsDisplay
                results={generationResults}
                onReset={() => {
                  setCurrentStep('upload');
                  setDocuments([]);
                  setGenerationResults(null);
                }}
              />
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-light-300">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Brain className="w-8 h-8 text-primary-500" />
            <span className="text-2xl font-bold text-primary-700">
              EvolSynth
            </span>
          </div>
          <p className="text-primary-700 mb-4">
            Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology
          </p>
          <p className="text-primary-600 text-sm">
            Built with ❤️ by Ovo Okpubuluku • Powered by OpenAI & LangChain
          </p>
        </div>
      </footer>
    </main>
  );
}
