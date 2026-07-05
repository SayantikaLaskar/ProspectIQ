import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Bot, ChevronLeft, ChevronRight, Radar, ScanLine, Wallet } from 'lucide-react'
import { spotlightMove } from '../ui'

const SLIDES = [
  { icon: Wallet, tag: 'Engine 01', title: 'Income X-ray',
    body: 'Reconstructs true monthly income from salary credits and business inflows — separating signal from noise with a volatility-aware haircut.',
    stat: '42% → 8%', statLabel: 'self-employed income error vs declared' },
  { icon: Radar, tag: 'Engine 02', title: 'Intent radar',
    body: "Scores per-product buying propensity and pinpoints the 'why-now' trigger — a renter building a corpus, an EMI just closed, a dealer enquiry.",
    stat: 'per-product', statLabel: 'propensity + why-now trigger' },
  { icon: ScanLine, tag: 'Engine 03', title: 'Repayment capacity',
    body: 'Detects existing EMIs and obligations to compute FOIR, disposable income and a defensible eligible amount for every product.',
    stat: 'FOIR-driven', statLabel: 'eligible amount per product' },
  { icon: Bot, tag: 'Agentic', title: 'RM copilot',
    body: 'Five role-specialised agents write the pitch, prep objections, run an RBI/DPDP compliance guardrail and draft the underwriting note.',
    stat: '5 agents', statLabel: 'pitch · objections · compliance · underwriting' },
]

export default function FeatureCarousel() {
  const [i, setI] = useState(0)
  const [dir, setDir] = useState(1)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    if (paused) return
    const t = setInterval(() => { setDir(1); setI((v) => (v + 1) % SLIDES.length) }, 4600)
    return () => clearInterval(t)
  }, [paused])

  const go = (d: number) => { setDir(d); setI((v) => (v + d + SLIDES.length) % SLIDES.length) }
  const s = SLIDES[i]
  const Icon = s.icon

  return (
    <div
      onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)} onMouseMove={spotlightMove}
      className="spotlight relative overflow-hidden rounded-3xl glass p-6 sm:p-8"
    >
      <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-emerald-500/10 blur-3xl" />

      <div className="relative flex min-h-[240px] flex-col">
        <div className="flex-1">
          <AnimatePresence mode="wait" custom={dir}>
            <motion.div key={i} custom={dir}
              initial={{ opacity: 0, x: dir * 36 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: dir * -36 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}>
              <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-emerald-400">{s.tag}</div>
              <div className="mt-4 flex items-center gap-3">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400/20 to-cyan-500/10 text-emerald-300 ring-1 ring-emerald-400/20">
                  <Icon className="h-5 w-5" />
                </span>
                <h3 className="font-display text-xl font-bold text-white sm:text-2xl">{s.title}</h3>
              </div>
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-300 sm:text-[15px]">{s.body}</p>
              <div className="mt-5 flex flex-wrap items-baseline gap-x-3 gap-y-1">
                <span className="gradient-text font-display text-2xl font-extrabold sm:text-3xl">{s.stat}</span>
                <span className="text-sm text-slate-400">{s.statLabel}</span>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-white/[0.06] pt-4">
          <div className="flex gap-1.5">
            {SLIDES.map((_, k) => (
              <button key={k} aria-label={`slide ${k + 1}`} onClick={() => { setDir(k > i ? 1 : -1); setI(k) }}
                className={`h-1.5 rounded-full transition-all ${k === i ? 'w-6 bg-emerald-400' : 'w-1.5 bg-white/20 hover:bg-white/40'}`} />
            ))}
          </div>
          <div className="flex items-center gap-2">
            <button aria-label="previous" onClick={() => go(-1)} className="rounded-full border border-white/10 bg-white/5 p-1.5 text-slate-300 transition hover:bg-white/10"><ChevronLeft className="h-4 w-4" /></button>
            <button aria-label="next" onClick={() => go(1)} className="rounded-full border border-white/10 bg-white/5 p-1.5 text-slate-300 transition hover:bg-white/10"><ChevronRight className="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </div>
  )
}
