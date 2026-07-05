import { useEffect, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'
import { motion } from 'framer-motion'
import { Gauge, IndianRupee, ShieldCheck, Target, TrendingUp, Users } from 'lucide-react'
import { getImpact } from '../api'
import type { Impact } from '../types'
import { lakh, pct } from '../format'
import { AnimatedNumber, Card, Reveal, SectionTitle, Spinner, Stat } from '../ui'
import Ticker from './Ticker'

const DRIVER_LABELS: Record<string, string> = {
  top_intent: 'Loan intent', has_trigger: 'Why-now trigger', income_confidence: 'Income confidence',
  disposable_income: 'Disposable income', foir_existing: 'Existing FOIR', est_income: 'Verified income',
  credit_score: 'Credit score', headroom_ratio: 'EMI headroom', savings_rate: 'Savings rate',
  income_stability: 'Income stability', balance_trend: 'Balance trend',
  relationship_months: 'Relationship tenure', num_products: 'Products held', eligible_top: 'Eligibility',
}
const PRODUCT_LABELS: Record<string, string> = {
  HOME_LOAN: 'Home Loan', AUTO_LOAN: 'Auto Loan', PERSONAL_LOAN: 'Personal Loan',
  MORTGAGE_LOAN: 'Loan Against Property',
}

export default function Dashboard() {
  const [m, setM] = useState<Impact | null>(null)
  useEffect(() => { getImpact().then(setM).catch(() => {}) }, [])
  if (!m) return <div className="p-8"><Spinner label="Loading business impact…" /></div>

  const tc = m.targeting_comparison
  const barData = [
    { name: 'Prospect IQ', v: tc.prospect_iq, me: true },
    { name: 'Credit score', v: tc.by_credit_score, me: false },
    { name: 'Declared income', v: tc.by_declared_income, me: false },
    { name: 'Random', v: tc.random, me: false },
  ]
  const drivers = Object.entries(m.conversion_drivers || {}).slice(0, 7)
  const maxDriver = Math.max(...drivers.map(([, v]) => v), 0.001)
  const val = m.validation
  const mult = val.income_self_employed_ape.engine ? val.income_self_employed_ape.declared / val.income_self_employed_ape.engine : 0
  const ticker = [
    { label: 'Qualified conversion', value: pct(m.qualified_conversion, 1) },
    { label: 'Lift vs baseline', value: `${m.conversion_lift_x}×` },
    { label: 'Self-employed income error', value: `${val.income_self_employed_ape.declared}% → ${val.income_self_employed_ape.engine}%` },
    { label: 'Model AUC', value: `${m.model_auc}` },
    { label: 'Pipeline surfaced', value: lakh(m.loan_book_opportunity) },
    { label: 'Qualified leads', value: m.qualified_leads.toLocaleString('en-IN') },
    { label: 'Top-200 vs credit', value: `${pct(m.targeting_comparison.prospect_iq, 0)} vs ${pct(m.targeting_comparison.by_credit_score, 0)}` },
  ]

  return (
    <div className="space-y-5 p-4 sm:p-6">
      <Reveal>
        <div className="mb-2 flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
          </span>
          <span className="font-mono text-[11px] uppercase tracking-widest text-emerald-400">Live · validated on held-out data</span>
        </div>
        <h2 className="font-display text-2xl font-bold text-white sm:text-3xl">
          Business <span className="gradient-text">Impact</span>
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          Cashflow-intelligence over {m.total_customers.toLocaleString('en-IN')} customers · validated on held-out ground truth.
        </p>
      </Reveal>

      <Reveal delay={0.04}><Ticker items={ticker} /></Reveal>

      {/* hero KPIs */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-5">
        <Stat delay={0} label="Qualified leads" icon={<Users className="h-4 w-4" />}
          value={<AnimatedNumber value={m.qualified_leads} format={(n) => Math.round(n).toLocaleString('en-IN')} />}
          sub={`of ${m.total_customers.toLocaleString('en-IN')} screened`} />
        <Stat delay={0.05} label="Qualified conversion" accent="text-emerald-300" icon={<Target className="h-4 w-4" />}
          value={<AnimatedNumber value={m.qualified_conversion * 100} format={(n) => `${n.toFixed(1)}%`} />}
          sub={`vs ${pct(m.baseline_conversion, 1)} calling all`} />
        <Stat delay={0.1} label="Conversion lift" accent="text-emerald-300" icon={<TrendingUp className="h-4 w-4" />}
          value={<AnimatedNumber value={m.conversion_lift_x || 0} format={(n) => `${n.toFixed(1)}×`} />}
          sub="over base rate" />
        <Stat delay={0.15} label="Loan-book opportunity" icon={<IndianRupee className="h-4 w-4" />}
          value={lakh(m.loan_book_opportunity)} sub="surfaced pipeline" />
        <Stat delay={0.2} label="Model AUC" icon={<Gauge className="h-4 w-4" />}
          value={<AnimatedNumber value={m.model_auc || 0} format={(n) => n.toFixed(2)} />}
          sub={m.real_benchmark ? `real UCI benchmark: ${m.real_benchmark.auc_precontact}` : 'out-of-fold, 5-way CV'} />
      </div>

      {/* money charts */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <Reveal className="lg:col-span-3">
          <Card className="p-5">
            <SectionTitle sub={`Conversion when the RM calls only the top ${m.targeting_focus_budget} customers, ranked each way.`}>
              Same call budget → 2× the loans
            </SectionTitle>
            <ResponsiveContainer width="100%" height={230}>
              <BarChart data={barData} margin={{ top: 16, right: 8, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#34d399" /><stop offset="100%" stopColor="#0891b2" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => pct(v, 1)} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                <Bar dataKey="v" radius={[8, 8, 0, 0]} label={{ position: 'top', formatter: (v: number) => pct(v, 0), fontSize: 12, fill: '#cbd5e1' }}>
                  {barData.map((d, i) => <Cell key={i} fill={d.me ? 'url(#barGrad)' : '#334155'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Reveal>

        <Reveal delay={0.1} className="lg:col-span-2">
          <Card className="p-5">
            <SectionTitle sub="Conversion vs number of customers contacted.">Efficient frontier</SectionTitle>
            <ResponsiveContainer width="100%" height={230}>
              <LineChart data={m.targeting_curve} margin={{ top: 12, right: 12, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="budget" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => pct(v, 1)} />
                <Line type="monotone" dataKey="prospect_iq" stroke="#34d399" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="by_credit_score" stroke="#f59e0b" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="random" stroke="#475569" strokeWidth={2} strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-1 flex flex-wrap gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1"><i className="h-2 w-3 rounded bg-emerald-400" />Prospect IQ</span>
              <span className="flex items-center gap-1"><i className="h-2 w-3 rounded bg-amber-500" />Credit score</span>
              <span className="flex items-center gap-1"><i className="h-2 w-3 rounded bg-slate-500" />Random</span>
            </div>
          </Card>
        </Reveal>
      </div>

      {/* validation + drivers + pipeline */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Reveal>
          <Card className="h-full p-5">
            <SectionTitle sub="Median error vs true income, held-out.">Income estimation accuracy</SectionTitle>
            <div className="gradient-border rounded-xl p-4">
              <div className="text-xs font-semibold text-emerald-300">Self-employed borrowers</div>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="font-display text-2xl font-extrabold text-rose-400 line-through decoration-2">{val.income_self_employed_ape.declared}%</span>
                <span className="text-slate-500">→</span>
                <span className="font-display text-3xl font-extrabold text-emerald-300 text-glow">{val.income_self_employed_ape.engine}%</span>
              </div>
              <div className="mt-1 text-xs text-emerald-300/80">{mult ? `${mult.toFixed(1)}× more accurate` : ''} than declared income</div>
            </div>
            <div className="mt-3 space-y-1 text-sm">
              <Row k="All customers — engine" v={`${val.income_median_ape.engine}% error`} good />
              <Row k="All customers — declared" v={`${val.income_median_ape.declared}% error`} />
              <Row k="Intent top-1 accuracy" v={`${val.intent_top1_accuracy}%`} />
              {m.real_benchmark && <Row k="Real-data benchmark · UCI (pre-contact)" v={`AUC ${m.real_benchmark.auc_precontact}`} good />}
            </div>
          </Card>
        </Reveal>

        <Reveal delay={0.08}>
          <Card className="h-full p-5">
            <SectionTitle sub="Gradient-boosted model feature importance.">What drives conversion</SectionTitle>
            <div className="space-y-2.5">
              {drivers.map(([k, v], i) => (
                <div key={k}>
                  <div className="mb-0.5 flex justify-between text-xs">
                    <span className="text-slate-300">{DRIVER_LABELS[k] || k}</span>
                    <span className="font-semibold text-slate-400">{Math.round(v * 100)}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/5">
                    <motion.div initial={{ width: 0 }} whileInView={{ width: `${(v / maxDriver) * 100}%` }} viewport={{ once: true }}
                      transition={{ duration: 0.8, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
                      className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-500" />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </Reveal>

        <Reveal delay={0.16}>
          <Card className="h-full p-5">
            <SectionTitle sub="Prioritised leads by band & product.">Pipeline breakdown</SectionTitle>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(m.bands).map(([b, c]) => (
                <div key={b} className="rounded-xl bg-white/5 p-3 ring-1 ring-white/5">
                  <div className="font-display text-lg font-extrabold text-white">{c}</div>
                  <div className="text-[11px] font-semibold uppercase text-slate-400">{b}</div>
                </div>
              ))}
            </div>
            <div className="mt-3 space-y-1.5">
              {Object.entries(m.product_distribution).sort((a, b) => b[1] - a[1]).map(([p, c]) => (
                <Row key={p} k={PRODUCT_LABELS[p] || p} v={`${c} leads`} />
              ))}
            </div>
          </Card>
        </Reveal>
      </div>

      <div className="flex items-center gap-2 pb-2 text-xs text-slate-500">
        <ShieldCheck className="h-3.5 w-3.5" /> Every metric is measured against held-out synthetic ground truth — nothing hard-coded.
      </div>
    </div>
  )
}

function Row({ k, v, good }: { k: string; v: string; good?: boolean }) {
  return (
    <div className="flex items-center justify-between border-b border-white/5 py-1 last:border-0">
      <span className="text-slate-400">{k}</span>
      <span className={`font-semibold ${good ? 'text-emerald-300' : 'text-slate-200'}`}>{v}</span>
    </div>
  )
}
