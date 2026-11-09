import React from "react";

const tabs = [
  { id: "dashboard", label: "Dashboard" },
  { id: "base", label: "Base Settings" },
  { id: "ffb", label: "FFB Equalizer" },
  { id: "profiles", label: "Profiles" },
];

export default function SideNav({ active, onChange }: { active: string; onChange: (t: string) => void }) {
  return (
    <aside className="w-64 h-[calc(100vh-2.5rem)] pt-10 bg-[#0b0b14] border-r border-white/5 flex flex-col shrink-0">
      <div className="p-6">
        <h1 className="text-xl font-black tracking-tighter text-white leading-none">
          PXN <span className="text-[#ff2a2a]">PIT</span>
        </h1>
        <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 mt-1">Custom Manager</p>
      </div>
      <nav className="flex-1 px-3 space-y-1">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => onChange(t.id)}
            className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
              active === t.id
                ? "bg-gradient-to-r from-[#ff2a2a]/10 to-transparent text-[#ff2a2a] shadow-[inset_2px_0_0_#ff2a2a]"
                : "text-slate-400 hover:text-white hover:bg-white/5"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Wheelbase Ready
        </div>
      </div>
    </aside>
  );
}
