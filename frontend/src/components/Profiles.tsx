import React from "react";

export default function Profiles() {
  return (
    <section className="space-y-8">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400 to-violet-600 flex items-center justify-center shadow-lg shadow-violet-400/20">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">Profiles</h2>
          <p className="text-xs text-slate-400">Save and load wheel configurations</p>
        </div>
      </div>
      <div className="bg-[#11111f] rounded-3xl p-8 border border-white/[0.06] shadow-2xl shadow-black/40 text-slate-400 text-sm">Profile management coming soon.</div>
    </section>
  );
}
