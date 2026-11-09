import React from "react";
import { debouncedUpdate } from "../api";

export default function BaseSettings({ state, onUpdate }: { state: any; onUpdate: () => void }) {
  const angle = state?.Rotation_Angle ?? 540;
  const ffb = state?.FFB_Gain ?? 50;

  return (
    <section className="space-y-10">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#ff2a2a] to-[#ff6b6b] flex items-center justify-center shadow-lg shadow-[#ff2a2a]/20">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
        </div>
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">Base Settings</h2>
          <p className="text-xs text-slate-400">Steering angle and overall force feedback gain</p>
        </div>
      </div>

      <div className="bg-[#11111f] rounded-3xl p-8 border border-white/[0.06] shadow-2xl shadow-black/40 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#ff2a2a]/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />

        <label className="block text-sm font-semibold text-slate-200 mb-3">Steering Angle <span className="text-[#ff2a2a] font-mono text-base ml-2">{angle}°</span></label>
        <input
          type="range"
          min={180}
          max={1080}
          step={10}
          value={angle}
          onChange={(e) => {
            const v = parseInt(e.target.value);
            debouncedUpdate("Rotation_Angle", v, () => onUpdate());
          }}
          className="w-full h-3 bg-gradient-to-r from-slate-800 via-[#ff2a2a]/60 to-slate-800 rounded-full appearance-none cursor-pointer accent-[#ff2a2a] hover:accent-[#ff6b6b] transition"
        />
        <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-mono">
          <span>180°</span><span>540°</span><span>1080°</span>
        </div>

        <div className="mt-10">
          <label className="block text-sm font-semibold text-slate-200 mb-3">FFB Gain <span className="text-[#00d4ff] font-mono text-base ml-2">{ffb}%</span></label>
          <input
            type="range"
            min={0}
            max={100}
            step={1}
            value={ffb}
            onChange={(e) => {
              const v = parseInt(e.target.value);
              debouncedUpdate("FFB_Gain", v, () => onUpdate());
            }}
            className="w-full h-3 bg-gradient-to-r from-slate-800 via-[#00d4ff]/60 to-slate-800 rounded-full appearance-none cursor-pointer accent-[#00d4ff] hover:accent-[#4deeff] transition"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-mono">
            <span>0%</span><span>50%</span><span>100%</span>
          </div>
        </div>
      </div>
    </section>
  );
}
