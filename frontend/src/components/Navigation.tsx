"use client";

import { useState } from "react";
import { Brain, Menu, X, Github, ExternalLink } from "lucide-react";

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToCenter = (targetId: string) => {
    const element = document.getElementById(targetId);
    if (element) {
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
      const offsetPosition = elementPosition - (window.innerHeight / 2) + (element.offsetHeight / 2);
      
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  const handleNavClick = (href: string, external?: boolean) => {
    if (external) return;
    
    if (href === "#docs") {
      scrollToCenter("docs");
    } else {
      // Default smooth scroll behavior for other links
      const element = document.querySelector(href);
      element?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const navItems = [
    { name: "Home", href: "#home" },
    { name: "Features", href: "#features" },
    { name: "API Docs", href: "#docs"},
    { name: "GitHub", href: "https://github.com/ovokpus/EvolSynth-API", external: true },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-lg border-b border-light-300 shadow-light-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-primary-400 rounded-xl blur opacity-30"></div>
              <div className="relative bg-gradient-to-r from-primary-600 to-primary-500 p-2 rounded-xl">
                <Brain className="w-6 h-6 text-white" />
              </div>
            </div>
            <div className="text-xl font-bold text-primary-700">
              EvolSynth
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center space-x-1 text-primary-700 hover:text-primary-600 transition-colors duration-200 group"
                target={item.external ? "_blank" : undefined}
                rel={item.external ? "noopener noreferrer" : undefined}
                onClick={(e) => {
                  if (!item.external) {
                    e.preventDefault();
                    handleNavClick(item.href);
                  }
                }}
              >
                <span>{item.name}</span>
                {item.external && (
                  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                )}
              </a>
            ))}
            
            {/* CTA Button */}
            <button 
              onClick={(e) => {
                e.preventDefault();
                handleNavClick("#interface");
              }}
              className="bg-primary-700 hover:bg-primary-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:shadow-purple-glow"
            >
              Try Now
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-primary-700 hover:text-primary-600 p-2 transition-colors duration-200"
            >
              {isMenuOpen ? <X className="w-6 h-6 text-primary-700" /> : <Menu className="w-6 h-6 text-primary-700" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-light-300">
            <div className="flex flex-col space-y-4">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="flex items-center justify-between text-primary-700 hover:text-primary-600 transition-colors duration-200 py-2 group"
                  target={item.external ? "_blank" : undefined}
                  rel={item.external ? "noopener noreferrer" : undefined}
                  onClick={(e) => {
                    setIsMenuOpen(false);
                    if (!item.external) {
                      e.preventDefault();
                      handleNavClick(item.href);
                    }
                  }}
                >
                  <span>{item.name}</span>
                  {item.external && (
                    <ExternalLink className="w-4 h-4 opacity-70 group-hover:opacity-100 transition-opacity duration-200" />
                  )}
                </a>
              ))}
              <button 
                onClick={() => {
                  setIsMenuOpen(false);
                  handleNavClick("#interface");
                }}
                className="bg-primary-700 hover:bg-primary-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:shadow-purple-glow mt-4 w-full"
              >
                Try Now
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
} 