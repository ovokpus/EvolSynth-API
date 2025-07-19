"use client";

import { useState } from "react";
import { ArrowRight, Sparkles, Zap, Brain } from "lucide-react";
import Documentation from "./Documentation";

export default function HeroSection() {
  const [showDocumentation, setShowDocumentation] = useState(false);

  const scrollToInterface = () => {
    const element = document.querySelector('#interface');
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  const openDocumentation = () => {
    // Option 1: Open external Swagger docs (current implementation)
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    window.open(`${baseUrl}/docs`, '_blank');
    
    // Option 2: Show modal documentation (uncomment to use)
    // setShowDocumentation(true);
  };

  return (
    <section id="home" className="relative pt-24 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200/20 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-fuchsia/15 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary-100/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative max-w-7xl mx-auto">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-primary-200 rounded-full px-4 py-2 mb-8 animate-fade-in shadow-light-lg">
            <Sparkles className="w-4 h-4 text-primary-600" />
            <span className="text-primary-700 text-sm font-medium">
              Powered by LangGraph & Evol-Instruct
            </span>
            <div className="w-2 h-2 bg-accent-emerald rounded-full animate-pulse"></div>
          </div>

          {/* Main headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold leading-tight mb-6 animate-slide-up">
            <span className="text-primary-700">
              Transform Documents into
            </span>
            <br />
            <span className="text-primary-600">
              Intelligent Datasets
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-primary-700 max-w-3xl mx-auto mb-12 leading-relaxed animate-slide-up" style={{ animationDelay: '200ms' }}>
            Revolutionary AI-powered synthetic data generation using{' '}
            <span className="text-primary-600 font-semibold">LangGraph-based Evol-Instruct methodology</span>.
            Create sophisticated evaluation datasets with three-tier question evolution and concurrent processing.
          </p>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto mb-12 animate-slide-up" style={{ animationDelay: '400ms' }}>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-700 mb-2">3x</div>
              <div className="text-primary-600 text-sm">Faster Generation</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-700 mb-2">4</div>
              <div className="text-primary-600 text-sm">Evolution Levels</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-700 mb-2">~ 99%</div>
              <div className="text-primary-600 text-sm">Quality Score</div>
            </div>
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16 animate-slide-up" style={{ animationDelay: '600ms' }}>
            <button
              onClick={scrollToInterface}
              className="group relative bg-primary-700 hover:bg-primary-600 text-white font-semibold px-8 py-4 rounded-xl transition-all duration-300 hover:shadow-purple-glow-lg hover:scale-105 flex items-center space-x-2"
            >
              <Zap className="w-5 h-5 text-white" />
              <span className="text-white">Start Generating</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300 text-white" />
            </button>
            
            <button 
              onClick={openDocumentation}
              className="group bg-white/80 hover:bg-white/90 backdrop-blur-sm border border-light-300 hover:border-primary-300 text-primary-700 font-medium px-8 py-4 rounded-xl transition-all duration-300 flex items-center space-x-2 shadow-light-lg hover:scale-105"
            >
              <Brain className="w-5 h-5 text-primary-700" />
              <span className="text-primary-700">View Documentation</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300 text-primary-700" />
            </button>
          </div>

          {/* Evolution showcase */}
          <div className="max-w-4xl mx-auto animate-slide-up" style={{ animationDelay: '800ms' }}>
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-light-300 p-8 shadow-light-lg">
              <h3 className="text-lg font-semibold text-primary-700 mb-6 text-center">
                See Evolution in Action
              </h3>
              
              <div className="space-y-4">
                {/* Evolution examples */}
                <div className="flex items-center space-x-4 p-4 bg-light-100/50 rounded-xl border border-light-200">
                  <div className="w-3 h-3 bg-accent-purple rounded-full"></div>
                  <div className="flex-1">
                    <div className="text-primary-600 text-sm mb-1">Original</div>
                    <div className="text-primary-700">What is a loan?</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-center">
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-px h-6 bg-gradient-to-b from-accent-purple to-accent-violet"></div>
                    <Brain className="w-6 h-6 text-primary-600" />
                    <div className="w-px h-6 bg-gradient-to-b from-accent-violet to-accent-fuchsia"></div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-primary-50 to-purple-50 rounded-xl border border-primary-200">
                  <div className="w-3 h-3 bg-gradient-to-r from-primary-600 to-accent-fuchsia rounded-full"></div>
                  <div className="flex-1">
                    <div className="text-primary-600 text-sm mb-1">Evolved (Reasoning Level)</div>
                    <div className="text-primary-700">If a student&apos;s dependency status changes mid-year, how would this impact their loan eligibility and disbursement schedule?</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Documentation Modal */}
      {showDocumentation && (
        <Documentation onClose={() => setShowDocumentation(false)} />
      )}
    </section>
  );
} 