import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { AnimatePresence, motion, useMotionValue, useScroll, useSpring, useTransform } from 'framer-motion'
import { ArrowRight, ShieldCheck, Sparkles } from 'lucide-react'
import { getImpact, listLeads } from '../api'
import type { Impact, LeadSummary } from '../types'
import { empLabel, inr, lakh, triggerLabel } from '../format'
import { AnimatedNumber, BandPill, Card, Reveal } from '../ui'
import Wordmark from './Wordmark'
import SignalsMarquee from './SignalsMarquee'
import FeatureCarousel from './FeatureCarousel'
import PipelineFlow from './PipelineFlow'
import Ticker from './Ticker'

const EASE = [0.22, 1, 0.36, 1] as const
const TYPED = ['cashflow.', 'real income.', 'buying intent.', 'repayment power.', 'why-now signals.']

const SAMPLE_LEADS: any[] = [
  { customer_id: 's1', name: 'Meghana Raju', city: 'Bengaluru', employment_type: 'self_employed', credit_score: 707, band: 'HOT', predicted_conversion: 0.96, estimated_monthly_income: 218983, income_uplift_pct: 64, recommended_product_label: 'Home Loan', recommended_amount: 13900000, why_now: { trigger: 'down_payment_building' } },
  { customer_id: 's2', name: 'Arjun Mehta', city: 'Pune', employment_type: 'salaried', credit_score: 768, band: 'HOT', predicted_conversion: 0.91, estimated_monthly_income: 142000, income_uplift_pct: 5, recommended_product_label: 'Auto Loan', recommended_amount: 1800000, why_now: { trigger: 'dealer_enquiry' } },
  { customer_id: 's3', name: 'Fatima Sheikh', city: 'Hyderabad', employment_type: 'mixed', credit_score: 721, band: 'WARM', predicted_conversion: 0.78, estimated_monthly_income: 98000, income_uplift_pct: 22, recommended_product_label: 'Personal Loan', recommended_amount: 900000, why_now: { trigger: 'large_expense' } },
]

function useTypewriter(words: string[]) {
  const [i, setI] = useState(0)
  const [text, setText] = useState('')
  const [deleting, setDeleting] = useState(false)
  useEffect(() => {
    const word = words[i % words.length]
    let delay = deleting ? 55 : 115
    if (!deleting && text === word) delay = 2400
    else if (deleting && text === '') delay = 500
    const t = setTimeout(() => {
      if (!deleting && text === word) setDeleting(true)
      else if (deleting && text === '') { setDeleting(false); setI((v) => (v + 1) % words.length) }
      else setText(deleting ? word.slice(0, text.length - 1) : word.slice(0, text.length + 1))
    }, delay)
    return () => clearTimeout(t)
  }, [text, deleting, i, words])
  return text
}

export default function Landing({ onEnter }: { onEnter: (view: 'dashboard' | 'leads') => void }) {
  const [m, setM] = useState<Impact | null>(null)
  const [leads, setLeads] = useState<LeadSummary[]>([])
  useEffect(() => {
    getImpact().then(setM).catch(() => {})
    listLeads({ min_conv: 0.5, limit: 6 }).then((d) => setLeads(d.leads)).catch(() => {})
  }, [])

  const typed = useTypewriter(TYPED)
  const { scrollY, scrollYProgress } = useScroll()
  const barX = useSpring(scrollYProgress, { stiffness: 120, damping: 30, mass: 0.3 })
  const orbsY = useTransform(scrollY, [0, 800], [0, 140])
  const mockY = useTransform(scrollY, [0, 700], [0, -60])
  const conv = m ? Math.round(m.qualified_conversion * 100) : 50

  const ticker = [
    { label: 'Qualified conversion', value: `${conv}%` },
    { label: 'Lift vs baseline', value: `${m?.conversion_lift_x ?? 2.9}×` },
    { label: 'Self-employed income error', value: `${m?.validation?.income_self_employed_ape?.declared ?? 42}% → ${m?.validation?.income_self_employed_ape?.engine ?? 8}%` },
    { label: 'Model AUC', value: `${m?.model_auc ?? 0.81}` },
    { label: 'Real UCI benchmark', value: `${m?.real_benchmark?.auc_precontact ?? 0.80}` },
    { label: 'Pipeline surfaced', value: lakh(m?.loan_book_opportunity ?? 1.03e9) },
  ]

  return (
    <div className="relative">
      <motion.div style={{ scaleX: barX }} className="fixed inset-x-0 top-0 z-50 h-0.5 origin-left bg-gradient-to-r from-emerald-400 to-cyan-500" />
      <motion.div style={{ y: orbsY }} className="pointer-events-none absolute inset-0 -z-[1]" />

      {/* nav */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <button onClick={() => onEnter('dashboard')}><Wordmark /></button>
        <div className="hidden items-center gap-7 text-sm text-slate-300 md:flex">
          <a href="#how" className="transition hover:text-white">How it works</a>
          <a href="#features" className="transition hover:text-white">Platform</a>
          <a href="#example" className="transition hover:text-white">Example</a>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-400">IDBI Innovate 2026</span>
        </div>
        <button onClick={() => onEnter('dashboard')}
          className="btn-shine group flex items-center gap-1.5 rounded-xl bg-white/5 px-4 py-2 text-sm font-semibold text-white ring-1 ring-white/15 transition hover:bg-white/10">
          Launch Console <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
        </button>
      </nav>

      {/* hero */}
      <section className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 pb-12 pt-10 lg:grid-cols-2 lg:pt-16">
        <div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: EASE }}
            className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">
            <Sparkles className="h-3.5 w-3.5" /> Problem Statement 2 · Prospect Assist AI
          </motion.div>

          <motion.h1 initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.05, ease: EASE }}
            className="mt-5 font-display text-4xl font-bold leading-[1.12] tracking-tight text-white sm:text-5xl">
            The lending engine that reads
            <span className="mt-1 block min-h-[1.2em] whitespace-nowrap">
              <span className="gradient-text">{typed}</span>
              <span className="ml-0.5 animate-blink font-light text-emerald-300">|</span>
            </span>
          </motion.h1>

          <motion.p initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.12, ease: EASE }}
            className="mt-6 max-w-xl text-base leading-relaxed text-slate-300 sm:text-lg">
            Traditional lending sees a declared number on a form. Prospect IQ sees the whole
            transaction story — finding genuinely-interested borrowers, proving their
            <span className="font-semibold text-white"> actual income</span>, and closing them with an agentic
            copilot. Conversion past <span className="font-semibold text-emerald-300">30%</span>.
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2, ease: EASE }}
            className="mt-8 flex flex-wrap items-center gap-3">
            <button onClick={() => onEnter('dashboard')}
              className="btn-shine group flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-500 px-5 py-3 text-sm font-bold text-slate-900 shadow-lg shadow-emerald-500/30 transition hover:shadow-emerald-500/50">
              Launch Console <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
            </button>
            <button onClick={() => onEnter('leads')}
              className="rounded-xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
              Explore the lead queue
            </button>
          </motion.div>
        </div>

        <motion.div style={{ y: mockY }}><Tilt><HeroMock leads={leads} /></Tilt></motion.div>
      </section>

      {/* signals marquee */}
      <section className="py-8">
        <div className="mx-auto max-w-7xl px-6">
          <p className="mb-4 text-center font-mono text-xs uppercase tracking-widest text-slate-500">Signals we read from the transaction stream</p>
        </div>
        <SignalsMarquee />
      </section>

      {/* live ticker */}
      <section className="mx-auto max-w-7xl px-6 py-6"><Ticker items={ticker} /></section>

      {/* pipeline */}
      <section id="how" className="mx-auto max-w-7xl px-6 py-16">
        <Reveal>
          <h2 className="font-display text-2xl font-bold text-white sm:text-3xl">From transactions to a booked loan</h2>
          <p className="mt-2 max-w-2xl text-slate-400">One deterministic pipeline — every stage explainable, every number auditable.</p>
        </Reveal>
        <div className="mt-8"><PipelineFlow /></div>
      </section>

      {/* feature carousel */}
      <section id="features" className="mx-auto max-w-7xl px-6 pb-8">
        <Reveal>
          <h2 className="font-display text-2xl font-bold text-white sm:text-3xl">Four engines. One decision.</h2>
          <p className="mt-2 max-w-2xl text-slate-400">Computed from raw transactions — with an evidence trail behind every score.</p>
        </Reveal>
        <Reveal delay={0.1} className="mt-8"><FeatureCarousel /></Reveal>
      </section>

      {/* worked example */}
      <section id="example" className="mx-auto max-w-7xl px-6 py-16">
        <Reveal>
          <h2 className="font-display text-2xl font-bold text-white sm:text-3xl">Watch it work — one prospect</h2>
          <p className="mt-2 max-w-2xl text-slate-400">Meghana, a self-employed customer in Bengaluru, declares ₹1.34L/mo. Here's what the transaction stream reveals.</p>
        </Reveal>
        <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {EXAMPLE.map((e, i) => (
            <Reveal key={e.step} delay={i * 0.1}>
              <Card hover className="h-full p-5">
                <div className="font-mono text-xs text-emerald-400">STEP {e.step}</div>
                <div className="mt-2 font-display font-bold text-white">{e.title}</div>
                <p className="mt-1.5 text-sm text-slate-400">{e.body}</p>
                <div className="mt-3 rounded-lg bg-white/5 p-2.5 ring-1 ring-white/10">
                  <div className="text-[10px] uppercase text-slate-500">{e.metricLabel}</div>
                  <div className="gradient-text font-display text-lg font-extrabold">{e.metric}</div>
                </div>
              </Card>
            </Reveal>
          ))}
        </div>
      </section>

      {/* outcome metrics */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
          <MetricBig value={conv} suffix="%" label="Qualified conversion" accent="text-emerald-300" />
          <MetricBig value={m?.conversion_lift_x ?? 2.9} suffix="×" d={1} label="Lift vs baseline" />
          <MetricBig value={m?.model_auc ?? 0.81} d={2} label="Model AUC (real UCI: 0.80)" accent="text-cyan-300" />
          <MetricBig text={lakh(m?.loan_book_opportunity ?? 1.03e9)} label="Pipeline surfaced" />
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-6 pb-20">
        <Reveal>
          <div className="flow-border relative overflow-hidden rounded-3xl p-10 text-center">
            <div className="absolute inset-0 -z-0 bg-gradient-to-br from-emerald-500/10 via-transparent to-cyan-500/10" />
            <h2 className="relative font-display text-2xl font-bold text-white sm:text-3xl">See the intelligence live</h2>
            <p className="relative mx-auto mt-2 max-w-lg text-slate-300">2,500 synthetic customers scored, ranked, and made actionable — with an agentic copilot on every lead.</p>
            <button onClick={() => onEnter('dashboard')}
              className="btn-shine relative mt-6 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-500 px-6 py-3 text-sm font-bold text-slate-900 shadow-lg shadow-emerald-500/30 transition hover:shadow-emerald-500/50">
              Launch Console <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </Reveal>
      </section>

      <footer className="border-t border-white/5 py-8 text-center text-xs text-slate-500">
        Prospect IQ · Built for IDBI Innovate 2026 — “Build. Integrate. Transform.” · Demo on privacy-safe synthetic data
      </footer>
    </div>
  )
}

const EXAMPLE = [
  { step: '1', title: 'Read the cashflow', body: 'UPI business inflows, cash deposits, rent, a steadily rising SIP — 12 months of it.', metricLabel: 'transactions analysed', metric: '~380 / customer' },
  { step: '2', title: 'Verify true income', body: 'Reconstructs income from inflows — far above the understated declared figure.', metricLabel: 'declared → verified', metric: '₹1.34L → ₹2.19L' },
  { step: '3', title: 'Read intent + why-now', body: 'Renter growing a corpus → home-loan intent, with a clear “building a down-payment” trigger.', metricLabel: 'best-fit product', metric: 'Home Loan' },
  { step: '4', title: 'Score & act', body: 'Ranked, eligible, and handed to the RM with a compliant, ready-to-send pitch.', metricLabel: 'predicted conversion', metric: '96%' },
]

function Tilt({ children }: { children: ReactNode }) {
  const rx = useMotionValue(0)
  const ry = useMotionValue(0)
  const srx = useSpring(rx, { stiffness: 150, damping: 18 })
  const sry = useSpring(ry, { stiffness: 150, damping: 18 })
  const onMove = (e: any) => {
    const r = e.currentTarget.getBoundingClientRect()
    ry.set(((e.clientX - r.left) / r.width - 0.5) * 10)
    rx.set(-((e.clientY - r.top) / r.height - 0.5) * 10)
  }
  return (
    <motion.div onMouseMove={onMove} onMouseLeave={() => { rx.set(0); ry.set(0) }}
      style={{ rotateX: srx, rotateY: sry, transformPerspective: 1000 }}>
      {children}
    </motion.div>
  )
}

function HeroMock({ leads }: { leads: LeadSummary[] }) {
  const list: any[] = leads && leads.length ? leads : SAMPLE_LEADS
  const [i, setI] = useState(0)
  useEffect(() => {
    if (list.length <= 1) return
    const t = setInterval(() => setI((v) => (v + 1) % list.length), 3400)
    return () => clearInterval(t)
  }, [list.length])
  const lead = list[i % list.length]

  return (
    <motion.div initial={{ opacity: 0, scale: 0.94, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.15, ease: EASE }} className="relative">
      <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-br from-emerald-500/20 to-cyan-500/10 blur-2xl" />
      <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}>
        <Card glow className="flow-border p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-emerald-400">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
              </span>
              Live lead queue
            </span>
            <span className="font-mono text-[10px] text-slate-500">{String((i % list.length) + 1).padStart(2, '0')} / {String(list.length).padStart(2, '0')}</span>
          </div>

          <AnimatePresence mode="wait">
            <motion.div key={lead.customer_id + i} initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -24 }}
              transition={{ duration: 0.4, ease: EASE }}>
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <div className="truncate font-display font-bold text-white">{lead.name}</div>
                  <div className="truncate text-xs text-slate-400">{lead.city} · {empLabel(lead.employment_type)} · CIBIL {lead.credit_score}</div>
                </div>
                <BandPill band={lead.band} pulse />
              </div>

              <div className="mt-4 flex items-end justify-between rounded-xl bg-white/5 p-3">
                <div>
                  <div className="text-[10px] uppercase text-slate-400">Predicted conversion</div>
                  <div className="font-display text-4xl font-extrabold text-emerald-300">{Math.round(lead.predicted_conversion * 100)}%</div>
                </div>
                <svg viewBox="0 0 120 40" className="h-10 w-28"><polyline fill="none" stroke="url(#g)" strokeWidth="2.5" points="0,32 20,28 40,30 60,20 80,22 100,10 120,6" /><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stopColor="#34d399" /><stop offset="1" stopColor="#22d3ee" /></linearGradient></defs></svg>
              </div>

              <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-lg bg-white/5 p-2.5">
                  <div className="text-[10px] uppercase text-slate-400">Verified income</div>
                  <div className="font-bold text-white">
                    {inr(lead.estimated_monthly_income)}
                    {Math.abs(lead.income_uplift_pct) >= 5 && <span className="ml-1 text-xs font-semibold text-emerald-300">+{Math.round(lead.income_uplift_pct)}%</span>}
                  </div>
                </div>
                <div className="rounded-lg bg-white/5 p-2.5">
                  <div className="text-[10px] uppercase text-slate-400">Best-fit</div>
                  <div className="font-bold text-white">{lead.recommended_product_label} · {lakh(lead.recommended_amount)}</div>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap gap-1.5">
                {lead.why_now && <span className="rounded-md bg-amber-500/15 px-2 py-0.5 text-[11px] text-amber-300 ring-1 ring-amber-500/30">{triggerLabel(lead.why_now.trigger)}</span>}
                <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/15 px-2 py-0.5 text-[11px] text-emerald-300 ring-1 ring-emerald-500/30"><ShieldCheck className="h-3 w-3" /> Compliance PASS</span>
              </div>
            </motion.div>
          </AnimatePresence>
        </Card>
      </motion.div>
    </motion.div>
  )
}

function MetricBig({ value, text, suffix = '', prefix = '', d = 0, label, accent = 'text-white' }: {
  value?: number; text?: string; suffix?: string; prefix?: string; d?: number; label: string; accent?: string
}) {
  return (
    <Card hover className="p-5">
      <div className={`font-display text-3xl font-extrabold sm:text-4xl ${accent}`}>
        {text ? text : <AnimatedNumber value={value ?? 0} format={(n) => `${prefix}${n.toFixed(d)}${suffix}`} />}
      </div>
      <div className="mt-1.5 text-xs text-slate-400">{label}</div>
    </Card>
  )
}
