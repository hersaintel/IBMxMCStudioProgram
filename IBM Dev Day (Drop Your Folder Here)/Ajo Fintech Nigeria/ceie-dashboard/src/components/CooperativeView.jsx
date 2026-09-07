import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, ShieldAlert, BadgeAlert, ArrowUpRight, 
  HelpCircle, RefreshCw, Layers, Sparkles
} from 'lucide-react';

export default function CooperativeView({ apiBase }) {
  const [loading, setLoading] = useState(true);
  const [coopData, setCoopData] = useState(null);

  const fetchCoopData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/alerts/cooperative/coop_north_01`);
      const data = await res.json();
      setCoopData(data);
    } catch (e) {
      console.error("Error fetching coop data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCoopData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-accentSky mb-4" />
        <p>Retrieving regional inflation logs and calculating hedging models...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Parallel Spread (90d)</p>
            <h3 className="text-2xl font-bold text-alertRed mt-1">
              +{coopData?.forecast_spreads?.["90_day_spread_pct"] || 25.0}%
            </h3>
            <p className="text-slate-500 text-[10px] mt-1">Widening parallel market gap</p>
          </div>
          <div className="bg-alertRed/10 p-3 rounded-lg text-alertRed">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Hedging Alerts</p>
            <h3 className="text-2xl font-bold text-accentSky mt-1">{coopData?.hedging_alerts?.length || 0} SMEs</h3>
            <p className="text-slate-500 text-[10px] mt-1">Urgent asset conversion suggested</p>
          </div>
          <div className="bg-accentSky/10 p-3 rounded-lg text-accentSky">
            <BadgeAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Default Risk Warnings</p>
            <h3 className="text-2xl font-bold text-alertYellow mt-1">{coopData?.loan_default_warnings?.length || 0} Importers</h3>
            <p className="text-slate-500 text-[10px] mt-1">Supply chain restructuring flagged</p>
          </div>
          <div className="bg-alertYellow/10 p-3 rounded-lg text-alertYellow">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-cardBg p-5 rounded-xl border border-borderSlate flex items-center justify-between shadow-lg">
          <div>
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Peak LGA Inflation</p>
            <h3 className="text-2xl font-bold text-white mt-1">34.2%</h3>
            <p className="text-slate-500 text-[10px] mt-1">Kano Municipal (Retail POS index)</p>
          </div>
          <div className="bg-slate-800 p-3 rounded-lg text-slate-300">
            <Layers className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Hedging Suggestions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <BadgeAlert className="w-5 h-5 text-accentSky" />
              <span>Watsonx-Driven Currency Hedging Alerts</span>
            </h2>
            <div className="space-y-4">
              {coopData?.hedging_alerts.map((alert) => (
                <div key={alert.entity_id} className="p-4 rounded-lg bg-slate-900/50 border border-borderSlate hover:bg-slate-800/40 transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-white text-sm">{alert.name}</h4>
                      <div className="flex gap-2 mt-1">
                        <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">ID: {alert.entity_id}</span>
                        <span className="text-[10px] bg-accentSky/15 text-accentSky px-1.5 py-0.5 rounded font-semibold">Exposure: {alert.exposure_ratio * 100}% NGN</span>
                      </div>
                    </div>
                    <span className="bg-accentSky/10 text-accentSky text-xs px-2.5 py-1 rounded font-bold">
                      Vulnerability Score: {alert.vulnerability_score}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-3 bg-slate-950 p-2.5 rounded border border-borderSlate/30 leading-relaxed font-mono">
                    <span className="text-accentSky font-bold uppercase block text-[10px] mb-1">Recommended Hedging Action:</span>
                    {alert.recommendation}
                  </p>
                </div>
              ))}
              {coopData?.hedging_alerts.length === 0 && (
                <p className="text-slate-400 text-xs py-6 text-center">No urgent hedging recommendations triggered at current exposure ratios.</p>
              )}
            </div>
          </div>

          {/* Default Risk Warnings */}
          <div className="bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-alertYellow" />
              <span>Trade Credit default warnings (Preemptive Restructuring)</span>
            </h2>
            <div className="space-y-4">
              {coopData?.loan_default_warnings.map((warn) => (
                <div key={warn.entity_id} className="p-4 rounded-lg bg-slate-900/50 border border-borderSlate">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-bold text-white text-sm">{warn.name}</h4>
                    <span className="text-alertRed font-mono font-bold text-xs uppercase bg-alertRed/10 border border-alertRed/25 px-2 py-0.5 rounded">
                      High Default Risk
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mb-3">{warn.risk_warning}</p>
                  <div className="flex flex-wrap gap-1">
                    {warn.factors.map((factor, idx) => (
                      <span key={idx} className="bg-slate-800 text-slate-300 text-[10px] px-2 py-0.5 rounded border border-borderSlate">
                        {factor}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              {coopData?.loan_default_warnings.length === 0 && (
                <p className="text-slate-400 text-xs py-6 text-center">All importer credit indicators remain inside risk tolerances.</p>
              )}
            </div>
          </div>
        </div>

        {/* Localized Micro-Inflation & Forecasting Panel */}
        <div className="space-y-6">
          
          {/* LGA Micro-inflation */}
          <div className="bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-alertYellow" />
              <span>Micro-Inflation LGA Tracker</span>
            </h2>
            <p className="text-slate-400 text-[11px] mb-3 leading-relaxed">
              Synthesized from regional POS agent network basket volumes. Flags erosion of rural savings.
            </p>
            <div className="space-y-2.5">
              {coopData?.micro_inflation_lga.map((item, idx) => (
                <div key={idx} className="bg-slate-950 p-2.5 rounded border border-borderSlate/30 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-slate-200 block">{item.lga}</span>
                    <span className="text-[10px] text-slate-500">{item.state} State</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold font-mono text-white block">+{item.cpi_increase_pct}%</span>
                    <span className={`text-[9px] px-1 rounded uppercase font-semibold ${
                      item.status === 'Critical' ? 'bg-alertRed/15 text-alertRed' :
                      item.status === 'High' ? 'bg-alertYellow/15 text-alertYellow' : 'bg-successGreen/15 text-successGreen'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Watsonx FX spread forecasts */}
          <div className="bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-accentSky" />
              <span>Watsonx USD/NGN Forecast Model</span>
            </h2>
            <div className="space-y-3.5 mt-4">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">7-Day predicted parallel spread:</span>
                  <span className="text-white font-mono font-bold">+{coopData?.forecast_spreads?.["7_day_spread_pct"]}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2">
                  <div className="bg-emerald-400 h-2 rounded-full" style={{ width: `${coopData?.forecast_spreads?.["7_day_spread_pct"] * 3}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">30-Day predicted parallel spread:</span>
                  <span className="text-white font-mono font-bold">+{coopData?.forecast_spreads?.["30_day_spread_pct"]}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2">
                  <div className="bg-amber-400 h-2 rounded-full" style={{ width: `${coopData?.forecast_spreads?.["30_day_spread_pct"] * 3}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">90-Day predicted parallel spread:</span>
                  <span className="text-white font-mono font-bold">+{coopData?.forecast_spreads?.["90_day_spread_pct"]}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2">
                  <div className="bg-alertRed h-2 rounded-full" style={{ width: `${coopData?.forecast_spreads?.["90_day_spread_pct"] * 3}%` }} />
                </div>
              </div>

              {coopData?.market_analysis && (
                <div className="mt-4 bg-slate-950 p-2.5 rounded border border-borderSlate/40 text-[10px] leading-relaxed text-slate-300 font-mono">
                  <span className="text-accentSky block font-bold mb-0.5">Granite-13b Commentary:</span>
                  {coopData.market_analysis}
                </div>
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
