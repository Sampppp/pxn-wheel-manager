import React from "react";

export default function Dashboard({ state }: { state: any }) {
  const angle = state?.Rotation_Angle ?? 540;
  const ffb = state?.FFB_Gain ?? 50;
  const connected = state?.connected ?? false;
  return (
    <section className="space-y-8">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-400/20">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">Dashboard</h2>
          <p className="text-xs text-slate-400">Live wheelbase telemetry</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#11111f] rounded-3xl p-6 border border-white/[0.06] shadow-2xl shadow-black/40">
          <div className="text-xs uppercase tracking-widest text-slate-500 mb-1">Rotation Angle</div>
          <div className="text-4xl font-black text-white">{angle}<span className="text-xl text-slate-400 font-medium">°</span></div>
        </div>
        <div className="bg-[#11111f] rounded-3xl p-6 border border-white/[0.06] shadow-2xl shadow-black/40">
          <div className="text-xs uppercase tracking-widest text-slate-500 mb-1">FFB Gain</div>
          <div className="text-4xl font-black text-[#00d4ff]">{ffb}<span className="text-xl text-slate-400 font-medium">%</span></div>
        </div>
        <div className="bg-[#11111f] rounded-3xl p-6 border border-white/[0.06] shadow-2xl shadow-black/40">
          <div className="text-xs uppercase tracking-widest text-slate-500 mb-1">Status</div>
          <div className={`text-2xl font-black ${connected ? "text-emerald-400" : "text-[#ff2a2a]"}`}>{connected ? "Connected" : "Disconnected"}</div>
        </div>
      </div>
    </section>
  );
}
