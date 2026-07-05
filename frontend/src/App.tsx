import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { BarChart3, Cpu, Home, LayoutDashboard, Menu, Users, X } from 'lucide-react'
import { getMeta } from './api'
import type { Meta } from './types'
import Aurora from './components/Aurora'
import CursorGlow from './components/CursorGlow'
import Wordmark from './components/Wordmark'
import Landing from './components/Landing'
import Dashboard from './components/Dashboard'
import LeadQueue from './components/LeadQueue'
import LeadDetail from './components/LeadDetail'

type View = 'dashboard' | 'leads'

export default function App() {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [entered, setEntered] = useState(false)
  const [view, setView] = useState<View>('dashboard')
  const [selected, setSelected] = useState<string | null>(null)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => { getMeta().then(setMeta).catch(() => {}) }, [])

  const nav = (v: View) => { setView(v); setSelected(null); setMobileOpen(false) }
  const enter = (v: View) => { setView(v); setSelected(null); setEntered(true) }

  return (
    <div className="relative min-h-screen">
      <Aurora />
      <CursorGlow />

      <AnimatePresence mode="wait">
        {!entered ? (
          <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
            <Landing onEnter={enter} />
          </motion.div>
        ) : (
          <motion.div key="app" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }} className="flex min-h-screen">
            {/* desktop sidebar */}
            <aside className="hidden w-64 shrink-0 border-r border-white/5 bg-white/[0.02] backdrop-blur-xl lg:flex lg:flex-col">
              <SidebarInner meta={meta} view={view} selected={selected} onNav={nav} onHome={() => setEntered(false)} />
            </aside>

            {/* mobile drawer */}
            <AnimatePresence>
              {mobileOpen && (
                <>
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    onClick={() => setMobileOpen(false)} className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden" />
                  <motion.aside initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }} transition={{ type: 'spring', damping: 26, stiffness: 240 }}
                    className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-white/10 bg-[#0a0f1d] lg:hidden">
                    <button onClick={() => setMobileOpen(false)} className="absolute right-3 top-4 text-slate-400 hover:text-white"><X className="h-5 w-5" /></button>
                    <SidebarInner meta={meta} view={view} selected={selected} onNav={nav} onHome={() => setEntered(false)} />
                  </motion.aside>
                </>
              )}
            </AnimatePresence>

            {/* main */}
            <main className="flex-1 overflow-x-hidden">
              <div className="sticky top-0 z-30 flex items-center justify-between border-b border-white/5 bg-[#05070f]/70 px-4 py-3 backdrop-blur-xl sm:px-6">
                <div className="flex items-center gap-3">
                  <button onClick={() => setMobileOpen(true)} className="text-slate-300 lg:hidden"><Menu className="h-5 w-5" /></button>
                  <div className="text-sm font-semibold text-slate-300">
                    {selected ? 'Prospect workspace' : view === 'dashboard' ? 'Business impact' : 'Prioritised prospects'}
                  </div>
                </div>
                <div className="hidden text-xs text-slate-500 sm:block">Cashflow-based lead generation · demo on synthetic data</div>
              </div>

              <AnimatePresence mode="wait">
                <motion.div key={selected ? `lead-${selected}` : view}
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}>
                  {selected ? (
                    <LeadDetail id={selected} meta={meta} onBack={() => setSelected(null)} />
                  ) : view === 'dashboard' ? (
                    <Dashboard />
                  ) : (
                    <LeadQueue meta={meta} onSelect={setSelected} />
                  )}
                </motion.div>
              </AnimatePresence>
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function SidebarInner({ meta, view, selected, onNav, onHome }: {
  meta: Meta | null; view: View; selected: string | null
  onNav: (v: View) => void; onHome: () => void
}) {
  return (
    <>
      <button onClick={onHome} className="block px-5 py-5 text-left">
        <Wordmark />
        <div className="mt-1 pl-4 text-[10px] text-slate-500">Retail Lending Intelligence</div>
      </button>

      <nav className="mt-2 flex-1 space-y-1 px-3">
        <NavItem active={view === 'dashboard' && !selected} onClick={() => onNav('dashboard')} icon={<LayoutDashboard className="h-4 w-4" />} label="Business Impact" />
        <NavItem active={view === 'leads' || !!selected} onClick={() => onNav('leads')} icon={<Users className="h-4 w-4" />} label="Lead Queue" />
      </nav>

      <div className="space-y-3 px-5 py-4 text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5"><Cpu className="h-3.5 w-3.5 text-emerald-400" /> Agents: <b className="text-slate-200">{meta?.llm.provider || '…'}</b></div>
        <div className="flex items-center gap-1.5"><BarChart3 className="h-3.5 w-3.5 text-cyan-400" /> {meta ? `${meta.total_customers?.toLocaleString('en-IN')} customers` : 'loading…'}</div>
        <button onClick={onHome} className="flex items-center gap-1.5 text-slate-500 transition hover:text-slate-300"><Home className="h-3.5 w-3.5" /> Back to landing</button>
        <div className="border-t border-white/5 pt-3 text-slate-500">IDBI Innovate 2026 · Prospect Assist AI</div>
      </div>
    </>
  )
}

function NavItem({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: ReactNode; label: string }) {
  return (
    <button onClick={onClick}
      className={`relative flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
        active ? 'bg-emerald-400/10 text-emerald-300 ring-1 ring-emerald-400/20' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}>
      {icon}{label}
    </button>
  )
}
