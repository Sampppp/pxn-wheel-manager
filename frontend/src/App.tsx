import React, { useEffect, useState, useCallback } from "react";
import SideNav from "./components/SideNav";
import Dashboard from "./components/Dashboard";
import BaseSettings from "./components/BaseSettings";
import FFBEqualizer from "./components/FFBEqualizer";
import Profiles from "./components/Profiles";
import { fetchSettings, debouncedUpdate } from "./api";

export default function App() {
  const [tab, setTab] = useState("dashboard");
  const [state, setState] = useState<any>({});

  const load = useCallback(async () => {
    try {
      const res = await fetchSettings();
      setState(res.data ?? {});
    } catch (e) {
      // silent fail
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 2000);
    return () => clearInterval(iv);
  }, [load]);

  const refresh = () => load();

  return (
    <div className="flex h-screen w-screen bg-[#0f0f1a] text-slate-100 overflow-hidden selection:bg-[#ff2a2a]/30">
      {/* Frameless drag handle / title bar */}
      <div className="fixed top-0 left-0 right-0 h-10 z-50 flex items-center justify-between px-4 bg-[#0f0f1a]/90 backdrop-blur-md border-b border-white/[0.06] select-none" style={{ WebkitAppRegion: 'drag' } as any}>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#ff2a2a]" />
          <span className="text-xs font-bold tracking-widest text-slate-300">PXN CUSTOM MANAGER</span>
        </div>
        <span className="text-[10px] text-slate-500">Drag to move · Resize from edges</span>
      </div>
      <SideNav active={tab} onChange={setTab} />
      <main className="flex-1 overflow-y-auto p-8 md:p-12 pt-16 scroll-smooth">
        <header className="mb-10 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-white">Pit House</h1>
            <p className="text-sm text-slate-400">Premium wheelbase control — dark mode active</p>
          </div>
          <button onClick={load} className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 text-xs font-bold uppercase tracking-widest border border-white/10 transition">Refresh</button>
        </header>

        {tab === "dashboard" && <Dashboard state={state} />}
        {tab === "base" && <BaseSettings state={state} onUpdate={refresh} />}
        {tab === "ffb" && <FFBEqualizer state={state} onUpdate={refresh} />}
        {tab === "profiles" && <Profiles />}
      </main>
    </div>
  );
}
