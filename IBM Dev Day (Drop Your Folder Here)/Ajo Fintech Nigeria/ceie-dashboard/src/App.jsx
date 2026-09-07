import React, { useState } from 'react';
import RegulatorView from './components/RegulatorView';
import CooperativeView from './components/CooperativeView';
import CalculatorView from './components/CalculatorView';
import { ShieldCheck, Cpu, Database, Network } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState("regulator");
  const [apiBase, setApiBase] = useState("http://localhost:8000");

  return (
    <div className="min-h-screen bg-darkBg text-slate-100 flex flex-col selection:bg-accentSky/30 selection:text-white">
      {/* Top Banner and Navigation */}
      <header className="border-b border-borderSlate bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Logo & Subhead */}
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-accentSky to-accentAmber p-2 rounded-xl text-slate-950 shadow-[0_0_15px_rgba(56,189,248,0.25)]">
              <Network className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent flex items-center gap-1.5">
                <span>Community Economic Intelligence Engine</span>
                <span className="text-[10px] font-semibold text-accentSky bg-accentSky/10 px-1.5 py-0.5 rounded uppercase border border-accentSky/25 font-mono">CEIE</span>
              </h1>
              <p className="text-xs text-slate-400">Nigeria-focused Volatility & Compliance Monitor | IBM Partner Architecture</p>
            </div>
          </div>

          {/* Integration Statuses */}
          <div className="flex flex-wrap items-center gap-3 text-[10px] bg-slate-900/60 p-2 rounded-lg border border-borderSlate/50 font-mono">
            <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-950 rounded">
              <Database className="w-3.5 h-3.5 text-accentSky" />
              <span className="text-slate-400">Match 360:</span>
              <span className="text-successGreen font-bold">CONNECTED</span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-950 rounded">
              <Cpu className="w-3.5 h-3.5 text-accentAmber" />
              <span className="text-slate-400">watsonx.ai:</span>
              <span className="text-successGreen font-bold">ACTIVE</span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-950 rounded">
              <ShieldCheck className="w-3.5 h-3.5 text-successGreen" />
              <span className="text-slate-400">DataStage:</span>
              <span className="text-successGreen font-bold">READY</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Tabs and Control Panel */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">
        
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/40 p-3 rounded-xl border border-borderSlate/55">
          {/* Dashboard Tabs */}
          <div className="flex bg-slate-950 p-1.5 rounded-lg border border-borderSlate/45">
            <button
              onClick={() => setActiveTab("regulator")}
              className={`px-4 py-2 text-xs sm:text-sm font-semibold rounded-md transition-all duration-200 ${
                activeTab === "regulator"
                  ? "bg-accentSky text-slate-950 shadow-[0_0_8px_rgba(56,189,248,0.3)]"
                  : "text-slate-400 hover:text-white hover:bg-slate-900"
              }`}
            >
              Regulator View (AML & Compliance)
            </button>
            <button
              onClick={() => setActiveTab("cooperative")}
              className={`px-4 py-2 text-xs sm:text-sm font-semibold rounded-md transition-all duration-200 ${
                activeTab === "cooperative"
                  ? "bg-accentSky text-slate-950 shadow-[0_0_8px_rgba(56,189,248,0.3)]"
                  : "text-slate-400 hover:text-white hover:bg-slate-900"
              }`}
            >
              Cooperative View (Economic Risk)
            </button>
            <button
              onClick={() => setActiveTab("calculator")}
              className={`px-4 py-2 text-xs sm:text-sm font-semibold rounded-md transition-all duration-200 ${
                activeTab === "calculator"
                  ? "bg-accentSky text-slate-950 shadow-[0_0_8px_rgba(56,189,248,0.3)]"
                  : "text-slate-400 hover:text-white hover:bg-slate-900"
              }`}
            >
              True FX Cost Calculator
            </button>
          </div>

          {/* Configuration Input */}
          <div className="flex items-center gap-2 self-stretch sm:self-auto bg-slate-950 p-1.5 rounded-lg border border-borderSlate/45">
            <span className="text-[10px] text-slate-500 font-mono pl-1.5">API:</span>
            <input 
              type="text" 
              value={apiBase} 
              onChange={(e) => setApiBase(e.target.value)}
              className="bg-slate-900 border border-borderSlate rounded px-2.5 py-1 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-accentSky w-full sm:w-44 font-mono"
            />
          </div>
        </div>

        {/* Tab Content Rendering */}
        <main className="animate-fadeIn">
          {activeTab === "regulator" ? (
            <RegulatorView apiBase={apiBase} />
          ) : activeTab === "cooperative" ? (
            <CooperativeView apiBase={apiBase} />
          ) : (
            <CalculatorView apiBase={apiBase} />
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-borderSlate/40 bg-slate-950/40 py-4 text-center mt-10">
        <p className="text-[10px] text-slate-500 font-mono">
          Community Economic Intelligence Engine &copy; 2026. Powered by IBM Cloud Pak for Data & Watsonx Governance.
        </p>
      </footer>
    </div>
  );
}
