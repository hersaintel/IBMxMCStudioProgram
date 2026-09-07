import React, { useState, useEffect } from 'react';
import { 
  Calculator, RefreshCw, AlertTriangle, CheckCircle, 
  HelpCircle, TrendingUp, Cpu, Info, DollarSign, Layers
} from 'lucide-react';

export default function CalculatorView({ apiBase }) {
  const [amountUsd, setAmountUsd] = useState(10000);
  const [loading, setLoading] = useState(true);
  const [calcData, setCalcData] = useState(null);
  const [selectedEntityId, setSelectedEntityId] = useState("ent_sme_00921");
  const [entityProfile, setEntityProfile] = useState(null);
  const [entitiesList, setEntitiesList] = useState([]);
  const [forecastData, setForecastData] = useState(null);

  // Fetch all needed data
  const loadCalculatorData = async () => {
    setLoading(true);
    try {
      // 1. Fetch calculator results
      const calcRes = await fetch(`${apiBase}/api/fx/calculator?amount_usd=${amountUsd}&entity_id=${selectedEntityId}`);
      const calcJson = await calcRes.json();
      setCalcData(calcJson);

      // 2. Fetch list of entities for profile inspection
      const entListRes = await fetch(`${apiBase}/api/entities`);
      const entListJson = await entListRes.json();
      setEntitiesList(entListJson);

      // 3. Fetch specific entity FX profile
      const profRes = await fetch(`${apiBase}/api/entities/${selectedEntityId}/fx-profile`);
      const profJson = await profRes.json();
      setEntityProfile(profJson);

      // 4. Fetch Watsonx spread forecast
      const fcRes = await fetch(`${apiBase}/api/watsonx/spread-forecast`);
      const fcJson = await fcRes.json();
      setForecastData(fcJson);
    } catch (e) {
      console.error("Error loading calculator view data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCalculatorData();
  }, [amountUsd, selectedEntityId]);

  if (loading && !calcData) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-accentSky mb-4" />
        <p>Loading real-time P2P exchange rate books and Watsonx time-series predictions...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-cardBg p-5 rounded-xl border border-borderSlate shadow-lg">
        
        {/* USD Value Input */}
        <div>
          <label className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-2">USD Amount to Convert</label>
          <div className="relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
              <DollarSign className="w-4 h-4" />
            </div>
            <input
              type="number"
              value={amountUsd}
              onChange={(e) => setAmountUsd(Math.max(1, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border border-borderSlate text-white text-sm rounded-lg focus:ring-accentSky focus:border-accentSky block w-full pl-9 p-2.5 outline-none font-mono"
              placeholder="Enter amount"
            />
          </div>
          <span className="text-[10px] text-slate-500 mt-1 block">Baseline for calculations (Default: $10,000)</span>
        </div>

        {/* Entity Selector (Match 360 Linked Profiles) */}
        <div>
          <label className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-2">Select SME Entity Profile</label>
          <select
            value={selectedEntityId}
            onChange={(e) => setSelectedEntityId(e.target.value)}
            className="bg-slate-900 border border-borderSlate text-white text-sm rounded-lg focus:ring-accentSky focus:border-accentSky block w-full p-2.5 outline-none"
          >
            {entitiesList.map((ent) => (
              <option key={ent.entity_id} value={ent.entity_id}>
                {ent.consolidated_attributes.primary_name} ({ent.entity_id})
              </option>
            ))}
          </select>
          <span className="text-[10px] text-slate-500 mt-1 block">Simulates cost using resolved conversion preferences</span>
        </div>

        {/* Selected Entity Match 360 Profile Summary */}
        <div className="bg-slate-950 p-3 rounded-lg border border-borderSlate/50 flex flex-col justify-between">
          <div className="flex justify-between items-start border-b border-borderSlate/30 pb-1.5 mb-1.5">
            <span className="text-[10px] text-accentSky font-bold uppercase tracking-wider">M360 Conversion Profile</span>
            <span className="bg-slate-800 text-[9px] text-slate-400 px-1.5 py-0.5 rounded font-mono">RESOLVED</span>
          </div>
          {entityProfile && (
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Primary Channel:</span>
                <span className="text-white font-bold font-mono">{entityProfile.fx_profile.primary_conversion_method}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Capital Markup above NAFEM:</span>
                <span className="text-alertYellow font-mono font-bold">+{entityProfile.fx_profile.estimated_cost_of_capital_markup_pct}%</span>
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Main Channels Comparison Table */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {calcData?.channels.map((channel, idx) => {
          const isOfficial = channel.compliance_rating === 'Green';
          const isRed = channel.compliance_rating === 'Red';
          
          return (
            <div 
              key={idx} 
              className={`bg-cardBg rounded-xl border p-5 shadow-lg flex flex-col justify-between relative overflow-hidden transition-all duration-200 ${
                isOfficial ? 'border-successGreen/40 hover:border-successGreen' : 
                isRed ? 'border-alertRed/40 hover:border-alertRed shadow-[0_0_15px_rgba(244,63,94,0.05)]' : 'border-borderSlate hover:border-accentSky'
              }`}
            >
              {/* Compliance Tag Banner */}
              <div className="absolute top-0 right-0">
                <span className={`text-[8px] font-bold px-2 py-0.5 uppercase tracking-wider block rounded-bl-lg font-mono ${
                  channel.compliance_rating === 'Green' ? 'bg-successGreen/20 text-successGreen border-l border-b border-successGreen/35' :
                  channel.compliance_rating === 'Yellow' ? 'bg-alertYellow/20 text-alertYellow border-l border-b border-alertYellow/35' :
                  'bg-alertRed/20 text-alertRed border-l border-b border-alertRed/35'
                }`}>
                  Tier {channel.compliance_rating} Compliance
                </span>
              </div>

              <div className="space-y-4">
                {/* Channel Header */}
                <div>
                  <h3 className="text-sm font-bold text-white pr-20 leading-snug">{channel.channel_name}</h3>
                  <div className="flex items-baseline gap-1 mt-1.5">
                    <span className="text-xs text-slate-400 font-mono">Rate:</span>
                    <span className="text-xl font-bold font-mono text-white">₦{channel.rate.toLocaleString()}</span>
                    <span className="text-[10px] text-slate-500">/USD</span>
                  </div>
                </div>

                {/* Calculation Returns */}
                <div className="bg-slate-950/60 p-3 rounded-lg border border-borderSlate/30 space-y-2">
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase tracking-wider block">Total Naira Returned</span>
                    <span className="text-lg font-bold font-mono text-white">₦{channel.total_returned_ngn.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-slate-400">Arbitrage vs Official:</span>
                    <span className={channel.arbitrage_savings_ngn > 0 ? "text-successGreen font-bold font-mono" : "text-slate-500 font-mono"}>
                      {channel.arbitrage_savings_ngn > 0 ? `+₦${channel.arbitrage_savings_ngn.toLocaleString()}` : "₦0.00"}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-slate-400">Loss vs Street (BDC):</span>
                    <span className={channel.exchange_loss_ngn > 0 ? "text-alertRed font-bold font-mono" : "text-slate-500 font-mono"}>
                      {channel.exchange_loss_ngn > 0 ? `-₦${channel.exchange_loss_ngn.toLocaleString()}` : "₦0.00"}
                    </span>
                  </div>
                </div>

                {/* Transaction details */}
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block font-semibold text-[10px] uppercase">Processing & Friction:</span>
                    <p className="text-slate-300 font-mono text-[11px] mt-0.5">{channel.friction_index}</p>
                  </div>
                </div>
              </div>

              {/* Regulatory warning note */}
              <div className="mt-5 pt-3 border-t border-borderSlate/40 text-[10px] text-slate-400 leading-normal flex items-start gap-1.5">
                {channel.compliance_rating === 'Red' ? (
                  <AlertTriangle className="w-3.5 h-3.5 text-alertRed flex-shrink-0 mt-0.5" />
                ) : channel.compliance_rating === 'Yellow' ? (
                  <Info className="w-3.5 h-3.5 text-alertYellow flex-shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle className="w-3.5 h-3.5 text-successGreen flex-shrink-0 mt-0.5" />
                )}
                <span>{channel.risk_description}</span>
              </div>

            </div>
          );
        })}
      </div>

      {/* Dynamic Graph and Watsonx predictions panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Watsonx Spread Forecast */}
        <div className="lg:col-span-2 bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center border-b border-borderSlate pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-accentSky animate-pulse" />
                <h2 className="text-lg font-bold text-white">Watsonx Granite Time-Series Prediction</h2>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">Model ID: {forecastData?.model_id}</span>
            </div>

            <p className="text-slate-300 text-xs mb-4 leading-relaxed">
              Using multivariate TinyTimeMixer (TTM) foundation models trained on P2P crypto order books and CBN official rates, Watsonx forecasts the widening spread between official peg and shadow market rates.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-slate-900 p-4 rounded-lg border border-borderSlate text-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">7-Day Spread Prediction</span>
                <span className="text-2xl font-extrabold font-mono text-emerald-400 block mt-1">
                  +{forecastData?.forecast_intervals?.["7_day_spread_pct"]}%
                </span>
                <div className="w-full bg-slate-950 rounded-full h-1 mt-2">
                  <div className="bg-emerald-400 h-1 rounded-full" style={{ width: `${forecastData?.forecast_intervals?.["7_day_spread_pct"] * 3}%` }} />
                </div>
              </div>
              
              <div className="bg-slate-900 p-4 rounded-lg border border-borderSlate text-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">30-Day Spread Prediction</span>
                <span className="text-2xl font-extrabold font-mono text-amber-400 block mt-1">
                  +{forecastData?.forecast_intervals?.["30_day_spread_pct"]}%
                </span>
                <div className="w-full bg-slate-950 rounded-full h-1 mt-2">
                  <div className="bg-amber-400 h-1 rounded-full" style={{ width: `${forecastData?.forecast_intervals?.["30_day_spread_pct"] * 3}%` }} />
                </div>
              </div>

              <div className="bg-slate-900 p-4 rounded-lg border border-borderSlate text-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">90-Day Spread Prediction</span>
                <span className="text-2xl font-extrabold font-mono text-alertRed block mt-1">
                  +{forecastData?.forecast_intervals?.["90_day_spread_pct"]}%
                </span>
                <div className="w-full bg-slate-950 rounded-full h-1 mt-2">
                  <div className="bg-alertRed h-1 rounded-full" style={{ width: `${forecastData?.forecast_intervals?.["90_day_spread_pct"] * 3}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-950/70 border border-borderSlate rounded-lg p-3.5 font-mono text-xs text-accentSky leading-relaxed">
            <div className="flex items-center gap-1.5 text-slate-400 border-b border-borderSlate/30 pb-1.5 mb-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-accentSky" />
              <span>Granite TTM Inbound Capital Flight Commentary</span>
            </div>
            <p className="text-slate-200">{forecastData?.granite_ts_analysis}</p>
          </div>
        </div>

        {/* Match 360 resolved shadow weight chart */}
        <div className="bg-cardBg rounded-xl border border-borderSlate p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 border-b border-borderSlate pb-3 mb-4">
              <Layers className="w-5 h-5 text-accentSky" />
              <h2 className="text-lg font-bold text-white">M360 resolved Liquidity Reliance</h2>
            </div>
            <p className="text-slate-400 text-xs mb-4 leading-normal">
              Probabilistic resolution mapping of the selected SME's bank identities to their shadow wallets.
            </p>

            {entityProfile ? (
              <div className="space-y-4 text-xs">
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-300 font-semibold">P2P Crypto Stablecoins</span>
                    <span className="text-white font-mono font-bold">
                      {entityProfile.fx_profile.source_liquidity_reliance.crypto_p2p_weight * 100}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2.5">
                    <div className="bg-accentSky h-2.5 rounded-full" style={{ width: `${entityProfile.fx_profile.source_liquidity_reliance.crypto_p2p_weight * 100}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-300 font-semibold">Street BDCs (Cash Abokis)</span>
                    <span className="text-white font-mono font-bold">
                      {entityProfile.fx_profile.source_liquidity_reliance.bdc_cash_weight * 100}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2.5">
                    <div className="bg-accentAmber h-2.5 rounded-full" style={{ width: `${entityProfile.fx_profile.source_liquidity_reliance.bdc_cash_weight * 100}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-300 font-semibold">Official Channels (NAFEM Peg)</span>
                    <span className="text-white font-mono font-bold">
                      {entityProfile.fx_profile.source_liquidity_reliance.official_nafem_weight * 100}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2.5">
                    <div className="bg-successGreen h-2.5 rounded-full" style={{ width: `${entityProfile.fx_profile.source_liquidity_reliance.official_nafem_weight * 100}%` }} />
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 text-xs py-10 text-center">No profile loaded.</p>
            )}
          </div>

          <div className="mt-6 bg-slate-900 p-3 rounded-lg border border-borderSlate/80 text-[10px] text-slate-400 leading-normal">
            <span className="text-accentSky block font-bold mb-1">Economic Arbitrage Insight:</span>
            While P2P and BDC rails offer higher returns, they expose entities to tax audit flags and bank account freezes. CEIE tracks these shadow footprints to calculate operational default risk limits.
          </div>
        </div>

      </div>
    </div>
  );
}
