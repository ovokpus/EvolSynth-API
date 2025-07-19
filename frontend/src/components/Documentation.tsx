"use client";

import { useState } from "react";
import { Book, Code, Play, ArrowRight, ExternalLink, Copy, CheckCircle } from "lucide-react";

interface DocumentationProps {
  onClose: () => void;
}

export default function Documentation({ onClose }: DocumentationProps) {
  const [activeSection, setActiveSection] = useState('overview');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = async (code: string, id: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(id);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Failed to copy code: ', err);
    }
  };

  const sections = [
    { id: 'overview', title: 'Overview', icon: Book },
    { id: 'quickstart', title: 'Quick Start', icon: Play },
    { id: 'api', title: 'API Reference', icon: Code },
    { id: 'examples', title: 'Examples', icon: ArrowRight },
  ];

  const generateExample = `import requests

# Generate synthetic data
response = requests.post("http://localhost:8000/generate", json={
    "documents": [
        {
            "content": "Machine learning algorithms enable computers to learn from data...",
            "metadata": {"source": "ml_intro.txt", "type": "text"}
        }
    ],
    "settings": {
        "execution_mode": "concurrent",
        "simple_evolution_count": 3,
        "multi_context_evolution_count": 2,
        "reasoning_evolution_count": 2,
        "temperature": 0.7
    },
    "max_iterations": 1
})

result = response.json()
print(f"Generated {len(result['evolved_questions'])} questions!")`;

  const evaluateExample = `# Evaluate quality
eval_response = requests.post("http://localhost:8000/evaluate", json={
    "evolved_questions": result["evolved_questions"],
    "question_answers": result["question_answers"],
    "question_contexts": result["question_contexts"],
    "evaluation_metrics": ["question_quality", "answer_accuracy", "evolution_effectiveness"]
})

evaluation = eval_response.json()
print(f"Quality scores: {evaluation['overall_scores']}")`;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-primary-50 border-b border-primary-200 p-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Book className="w-6 h-6 text-primary-600" />
            <h2 className="text-2xl font-bold text-primary-700">EvolSynth API Documentation</h2>
          </div>
          <button
            onClick={onClose}
            className="text-primary-500 hover:text-primary-700 transition-colors text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="flex h-full max-h-[calc(90vh-100px)]">
          {/* Sidebar */}
          <div className="w-64 bg-light-50 border-r border-light-200 p-4">
            <nav className="space-y-2">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                    activeSection === section.id
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'text-primary-600 hover:bg-light-100'
                  }`}
                >
                  <section.icon className="w-4 h-4" />
                  <span className="font-medium">{section.title}</span>
                </button>
              ))}
            </nav>

            <div className="mt-8 p-3 bg-primary-50 rounded-lg border border-primary-200">
              <h4 className="font-medium text-primary-700 mb-2">Interactive API Docs</h4>
              <p className="text-sm text-primary-600 mb-3">
                Explore the full API with Swagger UI
              </p>
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-1 text-primary-600 hover:text-primary-500 text-sm"
              >
                <ExternalLink className="w-3 h-3" />
                <span>Open Swagger Docs</span>
              </a>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {activeSection === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-bold text-primary-700 mb-4">Welcome to EvolSynth API</h3>
                  <p className="text-primary-600 mb-4">
                    EvolSynth API provides advanced synthetic data generation using LangGraph-based Evol-Instruct methodology. 
                    Transform your documents into sophisticated evaluation datasets with intelligent question evolution.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-accent-purple to-accent-violet text-white p-4 rounded-xl">
                    <h4 className="font-semibold mb-2">🎯 Smart Evolution</h4>
                    <p className="text-sm opacity-90">Three-tier question evolution: Simple → Multi-Context → Reasoning</p>
                  </div>
                  <div className="bg-gradient-to-br from-accent-violet to-accent-fuchsia text-white p-4 rounded-xl">
                    <h4 className="font-semibold mb-2">⚡ Lightning Fast</h4>
                    <p className="text-sm opacity-90">Concurrent processing - 3x faster generation</p>
                  </div>
                  <div className="bg-gradient-to-br from-accent-fuchsia to-accent-pink text-white p-4 rounded-xl">
                    <h4 className="font-semibold mb-2">🛡️ Quality Assured</h4>
                    <p className="text-sm opacity-90">Built-in LLM-as-judge evaluation with LangSmith tracking</p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'quickstart' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-primary-700 mb-4">Quick Start Guide</h3>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-start space-x-2">
                    <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-white text-xs font-bold">!</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-blue-800 mb-1">Prerequisites</h4>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• Backend running on <code className="bg-blue-100 px-1 rounded">http://localhost:8000</code></li>
                        <li>• OpenAI API key configured</li>
                        <li>• LangSmith API key for monitoring (optional)</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                      <h4 className="font-semibold text-primary-700">Health Check</h4>
                    </div>
                    <p className="text-primary-600 text-sm mb-2">Verify the API is running and all services are connected:</p>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <code className="text-green-400 text-sm">curl http://localhost:8000/health</code>
                      <button
                        onClick={() => copyToClipboard('curl http://localhost:8000/health', 'health')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'health' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                    <div className="mt-2 text-xs text-primary-600">
                      Expected response: <code className="bg-light-100 px-1 rounded">status: healthy, dependencies connected</code>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                      <h4 className="font-semibold text-primary-700">Get Sample Documents</h4>
                    </div>
                    <p className="text-primary-600 text-sm mb-2">Fetch sample documents to test the API:</p>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <code className="text-green-400 text-sm">curl http://localhost:8000/documents/sample</code>
                      <button
                        onClick={() => copyToClipboard('curl http://localhost:8000/documents/sample', 'sample')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'sample' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                    <div className="mt-2 text-xs text-primary-600">
                      Returns: <code className="bg-light-100 px-1 rounded">3 sample documents about financial aid</code>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                      <h4 className="font-semibold text-primary-700">Generate Synthetic Data</h4>
                    </div>
                    <p className="text-primary-600 text-sm mb-3">Choose your method:</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gradient-to-br from-primary-50 to-purple-50 border border-primary-200 rounded-lg p-4">
                        <h5 className="font-medium text-primary-700 mb-2">🎨 Use the Interface</h5>
                        <p className="text-sm text-primary-600 mb-3">Click "Start Generating" above for a guided experience</p>
                        <div className="text-xs text-primary-500">
                          ✓ Visual document upload<br/>
                          ✓ Interactive settings<br/>
                          ✓ Real-time results
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-light-50 to-primary-50 border border-light-300 rounded-lg p-4">
                        <h5 className="font-medium text-primary-700 mb-2">⚡ Use the API</h5>
                        <p className="text-sm text-primary-600 mb-3">Direct API calls for programmatic use</p>
                        <div className="text-xs text-primary-500">
                          ✓ Full control<br/>
                          ✓ Batch processing<br/>
                          ✓ Integration ready
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-6 h-6 bg-accent-emerald text-white rounded-full flex items-center justify-center text-sm font-bold">4</div>
                      <h4 className="font-semibold text-primary-700">Monitor with LangSmith</h4>
                    </div>
                    <p className="text-primary-600 text-sm mb-2">Track your evaluations and optimize prompts:</p>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <code className="text-purple-400 text-sm">🔗 https://smith.langchain.com/ → EvolSynth-API</code>
                      <button
                        onClick={() => copyToClipboard('https://smith.langchain.com/', 'langsmith')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'langsmith' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'api' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-primary-700 mb-4">API Endpoints</h3>
                
                <div className="space-y-4">
                  <div className="border border-light-300 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-mono">POST</span>
                      <code className="font-mono text-sm">/generate</code>
                    </div>
                    <p className="text-primary-600 text-sm">Generate synthetic evaluation data from documents</p>
                  </div>

                  <div className="border border-light-300 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-mono">POST</span>
                      <code className="font-mono text-sm">/evaluate</code>
                    </div>
                    <p className="text-primary-600 text-sm">Evaluate quality of generated synthetic data</p>
                  </div>

                  <div className="border border-light-300 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-mono">GET</span>
                      <code className="font-mono text-sm">/health</code>
                    </div>
                    <p className="text-primary-600 text-sm">Check API health and service status</p>
                  </div>

                  <div className="border border-light-300 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-mono">GET</span>
                      <code className="font-mono text-sm">/documents/sample</code>
                    </div>
                    <p className="text-primary-600 text-sm">Get sample documents for testing</p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'examples' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-primary-700 mb-4">Code Examples</h3>
                
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold text-primary-700 mb-3">Python Example - Generate Data</h4>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <pre className="text-green-400 text-sm overflow-x-auto">{generateExample}</pre>
                      <button
                        onClick={() => copyToClipboard(generateExample, 'generate')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'generate' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-primary-700 mb-3">Python Example - Evaluate Quality</h4>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <pre className="text-green-400 text-sm overflow-x-auto">{evaluateExample}</pre>
                      <button
                        onClick={() => copyToClipboard(evaluateExample, 'evaluate')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'evaluate' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-primary-700 mb-3">JavaScript/Node.js Example</h4>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <pre className="text-blue-400 text-sm overflow-x-auto">{`const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    documents: [{
      content: "Your document content here...",
      metadata: { source: "doc.txt", type: "text" }
    }],
    settings: {
      execution_mode: "concurrent",
      simple_evolution_count: 3,
      multi_context_evolution_count: 2,
      reasoning_evolution_count: 2,
      temperature: 0.7
    },
    max_iterations: 1
  })
});

const result = await response.json();
console.log(\`Generated \${result.evolved_questions.length} questions!\`);`}</pre>
                      <button
                        onClick={() => copyToClipboard(`const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    documents: [{
      content: "Your document content here...",
      metadata: { source: "doc.txt", type: "text" }
    }],
    settings: {
      execution_mode: "concurrent",
      simple_evolution_count: 3,
      multi_context_evolution_count: 2,
      reasoning_evolution_count: 2,
      temperature: 0.7
    },
    max_iterations: 1
  })
});

const result = await response.json();
console.log(\`Generated \${result.evolved_questions.length} questions!\`);`, 'javascript')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'javascript' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-primary-700 mb-3">cURL Example</h4>
                    <div className="bg-gray-900 rounded-lg p-4 relative">
                      <pre className="text-yellow-400 text-sm overflow-x-auto">{`curl -X POST "http://localhost:8000/generate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "documents": [{
      "content": "Your document content...",
      "metadata": {"source": "doc.txt", "type": "text"}
    }],
    "settings": {
      "execution_mode": "concurrent",
      "simple_evolution_count": 3,
      "multi_context_evolution_count": 2,
      "reasoning_evolution_count": 2,
      "temperature": 0.7
    },
    "max_iterations": 1
  }'`}</pre>
                      <button
                        onClick={() => copyToClipboard(`curl -X POST "http://localhost:8000/generate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "documents": [{
      "content": "Your document content...",
      "metadata": {"source": "doc.txt", "type": "text"}
    }],
    "settings": {
      "execution_mode": "concurrent",
      "simple_evolution_count": 3,
      "multi_context_evolution_count": 2,
      "reasoning_evolution_count": 2,
      "temperature": 0.7
    },
    "max_iterations": 1
  }'`, 'curl')}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-white"
                      >
                        {copiedCode === 'curl' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 