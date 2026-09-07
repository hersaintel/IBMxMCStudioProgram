import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, UserCheck, CreditCard, Search, Cpu, CheckCircle2, 
  AlertTriangle, ArrowRight, Eye, RefreshCw, Terminal, Layers
} from 'lucide-react';

export default function RegulatorView({ apiBase }) {
  const [loading, setLoading] = useState(true);
  const [complianceData, setComplianceData] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [nlpQuery, setNlpQuery] = useState("");
  const [nlpResponse, setNlpResponse] = useState("");
  const [nlpLoading, setNlpLoading] = useState(false);

  // Fetch data
  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/alerts/compliance`);
      const data = await res.json();
      setComplianceData(data);
      if (data.violations && data.violations.length > 0) {
        // Fetch detailed profile for the first violation as default selected
        fetchEntityDetail(data.violations[0].entity_id);
      }
    } catch (e) {
      console.error("Error fetching compliance data:", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchEntityDetail = async (entityId) => {
    try {
      const res = await fetch(`${apiBase}/api/entities/${entityId}`);
      const data = await res.json();
      setSelectedEntity(data);
    } catch (e) {
      console.error("Error fetching entity details:", e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Run a mock Granite NLP query
  const handleNlpSubmit = async (e, customQuery = null) => {
    if (e) e.preventDefault();
    const query = customQuery || nlpQuery;
    if (!query.trim()) return;

    setNlpLoading(true);
    setNlpResponse("");
    try {
      // Simulate Granite text response using Watsonx backend
      let endpoint = `${apiBase}/api/fx-forecast`;
      if (query.toLowerCase().includes("chidi") || query.toLowerCase().includes("922")) {
        endpoint = `${apiBase}/api/risk-assessment/ent_sme_00922`;
      } else if (query.toLowerCase().includes("seun") || query.toLowerCase().includes("921")) {
        endpoint = `${apiBase}/api/risk-assessment/ent_sme_00921`;
      }

      const res = await fetch(endpoint);
      const data = await res.json();
      
      // Adapt responses
      if (data.granite_explanation) {
        setNlpResponse(data.granite_explanation);
      } else if (data.granite_analysis) {
        setNlpResponse(data.granite_analysis);
      } else {
        setNlpResponse(`Granite: Analysis completed for query: "${query}". No critical anomalies detected outside of flagged records.`);
      }
    } catch (err) {
      setNlpResponse("Failed to query Watsonx Granite service.");
    } finally {
      setNlpLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-accentSky mb-4" />
        <p>Analyzing Match 360 graphs and compiling Watsonx compliance models...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Systemic Breaches</p>
            <h3 className="text-2xl font-bold text-alertRed mt-1">{complianceData?.total_breaches || 0} Entities</h3>
            <p className="text-slate-500 text-[10px] mt-1">Exceeding limits or layering wallets</p>
          </div>
          <div className="bg-alertRed/10 p-3 rounded-lg text-alertRed">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">CBN Allocation Cap</p>
            <h3 className="text-2xl font-bold text-white mt-1">$200,000 USD</h3>
            <p className="text-slate-500 text-[10px] mt-1">Maximum allocation limit YTD</p>
          </div>
          <div className="bg-accentSky/10 p-3 rounded-lg text-accentSky">
            <CreditCard className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">M360 Graph Links</p>
            <h3 className="text-2xl font-bold text-successGreen mt-1">7 Wallets/Accounts</h3>
            <p className="text-slate-500 text-[10px] mt-1">Resolved to 3 master entities</p>
          </div>
          <div className="bg-successGreen/10 p-3 rounded-lg text-successGreen">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate shadow-lg">
          <div className="flex items-center justify-between border-b border-borderSlate pb-2 mb-2">
            <div className="flex items-center gap-1.5 text-accentSky font-medium text-xs">
              <Cpu className="w-3.5 h-3.5" />
              <span>watsonx.governance</span>
            </div>
            <span className="bg-successGreen/25 text-successGreen text-[9px] px-1.5 py-0.5 rounded font-mono">ACTIVE</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div>
              <span className="text-slate-400">Drift:</span>
              <span className="text-white font-mono block">1.2% (Optimal)</span>
            </div>
            <div>
              <span className="text-slate-400">Fairness:</span>
              <span className="text-white font-mono block">98.4%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Compliance Violations List */}
        <div className="lg:col-span-2 bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-alertYellow" />
                <span>Flagged Transactions & Smurfing Alerts</span>
              </h2>
              <button 
                onClick={fetchData}
                className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
                title="Refresh compliance list"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            
            <div className="space-y-3 max-h-[350px] overflow-y-auto pr-1">
              {complianceData?.violations.map((violation) => (
                <div 
                  key={violation.entity_id}
                  onClick={() => fetchEntityDetail(violation.entity_id)}
                  className={`p-4 rounded-lg border transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                    selectedEntity?.entity_id === violation.entity_id 
                      ? 'bg-slate-800/60 border-accentSky' 
                      : 'bg-slate-900/40 border-borderSlate hover:bg-slate-800/30'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-sm text-white">{violation.name}</h4>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                        violation.cbn_tier === 'Red' 
                          ? 'bg-alertRed/10 text-alertRed border border-alertRed/25' 
                          : 'bg-alertYellow/10 text-alertYellow border border-alertYellow/25'
                      }`}>
                        Tier {violation.cbn_tier}
                      </span>
                    </div>
                    <p className="text-slate-400 text-xs mt-1">CAC Registration: {violation.cac_number} | BVN: {violation.bvn}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {violation.flags.map((flag, idx) => (
                        <span key={idx} className="bg-alertRed/20 text-alertRed text-[9px] px-1.5 py-0.5 rounded font-mono">
                          {flag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right flex md:flex-col items-end justify-between md:justify-center border-t md:border-t-0 border-borderSlate pt-2 md:pt-0">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">YTD FX Allocated</span>
                      <span className={`font-mono text-sm font-bold ${violation.total_fx_allocated_ytd > 200000 ? 'text-alertRed' : 'text-alertYellow'}`}>
                        ${violation.total_fx_allocated_ytd.toLocaleString('en-US', {minimumFractionDigits: 2})}
                      </span>
                    </div>
                    <button className="text-accentSky hover:text-white text-xs font-semibold flex items-center gap-1 mt-1.5">
                      <span>Inspect Record</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Watsonx Granite NLP query panel */}
          <div className="mt-6 border-t border-borderSlate pt-5">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
              <Terminal className="w-4 h-4 text-accentSky" />
              <span>Watsonx.ai Granite Copilot (NLP Query Shell)</span>
            </h3>
            
            <form onSubmit={handleNlpSubmit} className="flex gap-2">
              <input 
                type="text" 
                value={nlpQuery} 
                onChange={(e) => setNlpQuery(e.target.value)}
                placeholder="Ask Granite: 'Summarize Chidi Nwachukwu's risk profile' or 'Show capital flight patterns'..." 
                className="flex-1 bg-slate-900 border border-borderSlate rounded-lg px-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-accentSky"
              />
              <button 
                type="submit" 
                disabled={nlpLoading}
                className="bg-accentSky hover:bg-sky-500 disabled:bg-slate-700 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition flex items-center gap-1.5"
              >
                {nlpLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                <span>Ask</span>
              </button>
            </form>
            
            <div className="mt-3 flex gap-2 flex-wrap">
              <span className="text-xs text-slate-500 self-center">Suggestions:</span>
              <button 
                type="button"
                onClick={(e) => {
                  setNlpQuery("Show risk summary for entity ent_sme_00922");
                  handleNlpSubmit(e, "Show risk summary for entity ent_sme_00922");
                }}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] px-2 py-1 rounded border border-borderSlate transition"
              >
                "Summarize Chidi's violations"
              </button>
              <button 
                type="button"
                onClick={(e) => {
                  setNlpQuery("Forecast parallel market spread");
                  handleNlpSubmit(e, "Forecast parallel market spread");
                }}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] px-2 py-1 rounded border border-borderSlate transition"
              >
                "Forecast parallel USD/NGN spread"
              </button>
            </div>

            {nlpResponse && (
              <div className="mt-4 bg-slate-950/70 border border-borderSlate rounded-lg p-3 font-mono text-xs text-accentSky space-y-1.5 animate-fadeIn">
                <div className="flex items-center gap-1 text-slate-400 border-b border-borderSlate/30 pb-1 mb-1">
                  <Cpu className="w-3.5 h-3.5 text-accentSky" />
                  <span>watsonx-granite-13b-output</span>
                </div>
                <p className="leading-relaxed text-slate-200">{nlpResponse}</p>
              </div>
            )}
          </div>

        </div>

        {/* Match 360 Inspector Drawer */}
        <div className="bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 border-b border-borderSlate pb-3 mb-4">
              <UserCheck className="w-5 h-5 text-accentSky" />
              <h2 className="text-lg font-bold text-white">M360 Golden Record</h2>
            </div>

            {selectedEntity ? (
              <div className="space-y-4">
                {/* Entity Summary */}
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedEntity.consolidated_attributes.primary_name}</h3>
                  <div className="flex gap-2 mt-1.5">
                    <span className="bg-slate-800 text-slate-300 text-[10px] px-2 py-0.5 rounded border border-borderSlate">
                      BVN: {selectedEntity.consolidated_attributes.bvn}
                    </span>
                    <span className="bg-slate-800 text-slate-300 text-[10px] px-2 py-0.5 rounded border border-borderSlate">
                      CAC: {selectedEntity.consolidated_attributes.cac_number}
                    </span>
                  </div>
                </div>

                {/* Resolving Aliases */}
                <div className="bg-slate-900/50 p-3 rounded-lg border border-borderSlate/50">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">Resolved Aliases</span>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {selectedEntity.consolidated_attributes.alternate_names.map((name, idx) => (
                      <span key={idx} className="bg-slate-800 text-white text-[11px] px-2 py-0.5 rounded font-mono">
                        {name}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Linked Accounts & Wallets Graph */}
                <div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold mb-2">Linked Wallets (Identity Graph)</span>
                  <div className="space-y-2">
                    {selectedEntity.consolidated_attributes.linked_wallets.map((wallet, idx) => (
                      <div key={idx} className="bg-slate-950 p-2.5 rounded border border-borderSlate/30 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            wallet.source.includes("OPay") ? "bg-emerald-400" :
                            wallet.source.includes("Moniepoint") ? "bg-amber-400" : "bg-sky-400"
                          }`} />
                          <span className="font-semibold text-slate-300">{wallet.source}</span>
                        </div>
                        <span className="font-mono text-slate-500">{wallet.wallet_id || wallet.account_id}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Compliance Parameters */}
                <div className="border-t border-borderSlate pt-3 space-y-2.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Valid Form M:</span>
                    <span className={selectedEntity.compliance_metadata.has_valid_form_m ? "text-successGreen font-bold" : "text-alertRed font-bold"}>
                      {selectedEntity.compliance_metadata.has_valid_form_m ? "Yes" : "No"}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Import Category Tags:</span>
                    <span className="text-white font-mono text-[10px] text-right">
                      {selectedEntity.compliance_metadata.import_category_tags.join(', ')}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Naira Reserve Exposure:</span>
                    <span className="text-white font-bold">
                      {selectedEntity.exposure_metadata.currency_exposure_ratio * 100}% NGN
                    </span>
                  </div>
                </div>

              </div>
            ) : (
              <p className="text-slate-400 text-xs py-10 text-center">Select an entity on the left to inspect resolved master records.</p>
            )}
          </div>

          <div className="mt-6 bg-slate-900 p-3 rounded-lg border border-borderSlate text-[11px] text-slate-400">
            <span className="font-bold text-accentSky block mb-1">Entity Resolution Insight:</span>
            Probabilistic models resolve variations (e.g. Oluwaseun vs Seun) by cross-referencing NIN/BVN registers and historical geolocations, neutralizing smurfing attempts across agent terminals.
          </div>
        </div>

      </div>
    </div>
  );
}
