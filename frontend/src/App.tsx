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
      <SideNav active={tab} onChange={setTab} />
      <main className="flex-1 overflow-y-auto p-8 md:p-12 scroll-smooth">
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
