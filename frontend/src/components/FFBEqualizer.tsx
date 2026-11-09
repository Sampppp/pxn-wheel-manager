import React from "react";
import { debouncedUpdate } from "../api";

function SliderRow({ label, value, min, max, step, accent, onChange }: any) {
  return (
    <div className="group">
      <div className="flex justify-between items-end mb-2">
        <span className="text-sm font-medium text-slate-200">{label}</span>
        <span className={`font-mono text-sm font-bold ${accent}`}>{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className={`w-full h-2.5 rounded-full appearance-none cursor-pointer bg-gradient-to-r from-slate-800 via-${accent.replace("text-","")}/60 to-slate-800 transition accent-[${accent.replace("text-","")}]`}
        style={{ accentColor: accent === "text-[#ff2a2a]" ? "#ff2a2a" : accent === "text-[#00d4ff]" ? "#00d4ff" : "#a855f7" }}
      />
    </div>
  );
}

export default function FFBEqualizer({ state, onUpdate }: { state: any; onUpdate: () => void }) {
  const damper = state?.Mechanical_Damper ?? 30;
  const friction = state?.Friction ?? 20;
  const inertia = state?.Inertia ?? 40;
  const spring = state?.Spring ?? 50;

  return (
    <section className="space-y-10">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00d4ff] to-[#4deeff] flex items-center justify-center shadow-lg shadow-[#00d4ff]/20">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M19.07 4.93L4.93 19.07"/></svg>
        </div>
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">FFB Equalizer</h2>
          <p className="text-xs text-slate-400">Advanced force feedback tuning</p>
        </div>
      </div>

      <div className="bg-[#11111f] rounded-3xl p-8 border border-white/[0.06] shadow-2xl shadow-black/40 grid grid-cols-1 md:grid-cols-2 gap-8">
        <SliderRow label="Damper" value={damper} min={0} max={100} step={1} accent="text-[#ff2a2a]" onChange={(v: number) => debouncedUpdate("Mechanical_Damper", v, () => onUpdate())} />
        <SliderRow label="Friction" value={friction} min={0} max={100} step={1} accent="text-[#00d4ff]" onChange={(v: number) => debouncedUpdate("Friction", v, () => onUpdate())} />
        <SliderRow label="Inertia" value={inertia} min={0} max={100} step={1} accent="text-[#a855f7]" onChange={(v: number) => debouncedUpdate("Inertia", v, () => onUpdate())} />
        <SliderRow label="Spring" value={spring} min={0} max={100} step={1} accent="text-[#f59e0b]" onChange={(v: number) => debouncedUpdate("Spring", v, () => onUpdate())} />
      </div>
    </section>
  );
}
