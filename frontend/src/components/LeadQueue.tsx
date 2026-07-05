import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Sparkles, Zap } from 'lucide-react'
import { listLeads } from '../api'
import type { LeadSummary, Meta } from '../types'
import { bandDot, empLabel, inr, lakh, pct, triggerLabel } from '../format'
import { BandPill, Card, Reveal, Spinner } from '../ui'

export default function LeadQueue({ meta, onSelect }: { meta: Meta | null; onSelect: (id: string) => void }) {
  const [leads, setLeads] = useState<LeadSummary[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [product, setProduct] = useState('')
  const [band, setBand] = useState('')
  const [qualifiedOnly, setQualifiedOnly] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    setLoading(true)
    const t = setTimeout(() => {
      listLeads({ product, band, search, min_conv: qualifiedOnly ? 0.3 : undefined, limit: 60 })
        .then((d) => { setLeads(d.leads); setTotal(d.total) })
        .finally(() => setLoading(false))
    }, search ? 250 : 0)
    return () => clearTimeout(t)
  }, [product, band, qualifiedOnly, search])

  const selectCls = 'rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-200 outline-none focus:ring-2 focus:ring-emerald-400/40 [&>option]:bg-slate-900'

  return (
    <div className="space-y-5 p-4 sm:p-6">
      <Reveal>
        <h2 className="font-display text-2xl font-extrabold text-white sm:text-3xl">
          Lead <span className="gradient-text">Queue</span>
        </h2>
        <p className="mt-1 text-sm text-slate-400">{total.toLocaleString('en-IN')} prospects · ranked by predicted conversion</p>
      </Reveal>

      {/* filters */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 sm:flex-none">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search name / ID"
            className="w-full rounded-xl border border-white/10 bg-white/5 py-2 pl-9 pr-3 text-sm text-slate-200 outline-none focus:ring-2 focus:ring-emerald-400/40 sm:w-56" />
        </div>
        <select value={product} onChange={(e) => setProduct(e.target.value)} className={selectCls}>
          <option value="">All products</option>
          {meta?.products.map((p) => <option key={p.code} value={p.code}>{p.label}</option>)}
        </select>
        <select value={band} onChange={(e) => setBand(e.target.value)} className={selectCls}>
          <option value="">All bands</option>
          {['HOT', 'WARM', 'NURTURE', 'COLD'].map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
        <button onClick={() => setQualifiedOnly((q) => !q)}
          className={`flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-semibold ring-1 transition ${
            qualifiedOnly ? 'bg-emerald-400/15 text-emerald-300 ring-emerald-400/30' : 'bg-white/5 text-slate-400 ring-white/10'}`}>
          <Zap className="h-4 w-4" /> Qualified
        </button>
      </div>

      {loading ? (
        <div className="p-8"><Spinner label="Scoring prospects…" /></div>
      ) : leads.length === 0 ? (
        <Card className="p-8 text-sm text-slate-400">No leads match these filters.</Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
          {leads.map((l, i) => (
            <motion.button key={l.customer_id} onClick={() => onSelect(l.customer_id)}
              initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: Math.min(i * 0.02, 0.4), ease: [0.22, 1, 0.36, 1] }}
              whileHover={{ y: -3 }}
              className="group relative overflow-hidden rounded-2xl glass glass-hover p-4 text-left">
              <div className="absolute right-0 top-0 h-24 w-24 rounded-full bg-emerald-500/10 opacity-0 blur-2xl transition group-hover:opacity-100" />
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 shrink-0 rounded-full ${bandDot[l.band]}`} />
                    <span className="truncate font-semibold text-white">{l.name}</span>
                    <BandPill band={l.band} pulse />
                  </div>
                  <div className="mt-0.5 truncate text-xs text-slate-400">{l.city} · {empLabel(l.employment_type)} · CIBIL {l.credit_score}</div>
                </div>
                <div className="text-right">
                  <div className="font-display text-2xl font-extrabold text-emerald-300">{pct(l.predicted_conversion, 0)}</div>
                  <div className="text-[10px] uppercase text-slate-500">conversion</div>
                </div>
              </div>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-500" style={{ width: pct(l.predicted_conversion) }} />
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-sm">
                <div>
                  <div className="font-medium text-slate-200">{l.recommended_product_label}</div>
                  <div className="text-xs text-slate-400">{lakh(l.recommended_amount)} · {inr(l.indicative_emi)}/mo</div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-slate-200">{inr(l.estimated_monthly_income)}</div>
                  {Math.abs(l.income_uplift_pct) >= 5 && (
                    <div className={`text-xs font-semibold ${l.income_uplift_pct > 0 ? 'text-emerald-300' : 'text-slate-500'}`}>
                      {l.income_uplift_pct > 0 ? '+' : ''}{Math.round(l.income_uplift_pct)}% vs declared
                    </div>
                  )}
                </div>
              </div>

              {l.why_now && (
                <div className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-amber-500/10 px-2 py-1 text-xs font-medium text-amber-300 ring-1 ring-amber-500/20">
                  <Sparkles className="h-3 w-3" /> {triggerLabel(l.why_now.trigger)}
                </div>
              )}
            </motion.button>
          ))}
        </div>
      )}
    </div>
  )
}
