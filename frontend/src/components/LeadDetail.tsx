import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Line, LineChart, ResponsiveContainer, Tooltip, YAxis } from 'recharts'
import {
  ArrowLeft, BadgeCheck, Check, ClipboardCopy, MessageSquare, Sparkles,
  ShieldCheck, TriangleAlert, Wallet,
} from 'lucide-react'
import { getAgents, getLead, postPitch } from '../api'
import type { AgentBundle, LeadDetail as Lead, Meta } from '../types'
import { empLabel, gradeColor, inr, lakh, pct, triggerLabel } from '../format'
import { BandPill, Card, Reveal, ScoreBar, SectionTitle, Spinner, StatusChip } from '../ui'
import Chat from './Chat'

const PRODUCT_LABELS: Record<string, string> = {
  HOME_LOAN: 'Home Loan', AUTO_LOAN: 'Auto Loan', PERSONAL_LOAN: 'Personal Loan',
  MORTGAGE_LOAN: 'Loan Against Property',
}
const TABS = [
  { k: 'brief', label: 'Brief' }, { k: 'pitch', label: 'Pitch' },
  { k: 'objections', label: 'Objections' }, { k: 'compliance', label: 'Compliance' },
  { k: 'underwriting', label: 'Underwriting' }, { k: 'chat', label: 'Chat' },
]

export default function LeadDetail({ id, meta, onBack }: { id: string; meta: Meta | null; onBack: () => void }) {
  const [lead, setLead] = useState<Lead | null>(null)
  const [agents, setAgents] = useState<AgentBundle | null>(null)
  const [tab, setTab] = useState('brief')
  const [channel, setChannel] = useState('WHATSAPP')
  const [pitch, setPitch] = useState<AgentBundle['pitch'] | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    setLead(null); setAgents(null); setPitch(null); setTab('brief'); setChannel('WHATSAPP')
    getLead(id).then(setLead).catch(() => {})
    getAgents(id, 'WHATSAPP').then((a) => { setAgents(a); setPitch(a.pitch) }).catch(() => {})
  }, [id])

  const changeChannel = async (c: string) => {
    setChannel(c)
    try { setPitch(await postPitch(id, c)) } catch { /* keep old */ }
  }
  const copy = (t: string) => { navigator.clipboard?.writeText(t); setCopied(true); setTimeout(() => setCopied(false), 1500) }

  if (!lead) return <div className="p-8"><Spinner label="Loading prospect…" /></div>

  const inc = lead.income, aff = lead.affordability, intent = lead.intent, comp = lead.score_components
  const eligOrder = meta?.products.map((p) => p.code) || Object.keys(aff.eligibility)

  return (
    <div className="space-y-4 p-4 sm:p-6">
      <button onClick={onBack} className="flex items-center gap-1.5 text-sm font-medium text-slate-400 transition hover:text-slate-200">
        <ArrowLeft className="h-4 w-4" /> Back to queue
      </button>

      {/* header */}
      <Reveal>
        <Card className="p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="font-display text-2xl font-extrabold text-white">{lead.name}</h2>
                <BandPill band={lead.band} pulse />
                {lead.under_review && (
                  <span className="inline-flex items-center gap-1 rounded-md bg-amber-500/15 px-2 py-0.5 text-xs font-semibold text-amber-300 ring-1 ring-amber-500/30">
                    <TriangleAlert className="h-3 w-3" /> Refer to credit
                  </span>
                )}
              </div>
              <div className="mt-1 text-sm text-slate-400">
                {lead.customer_id} · {lead.age} yrs · {lead.city} (Tier {lead.city_tier}) · {empLabel(lead.employment_type)} · CIBIL {lead.credit_score} · {lead.relationship_months} mo
              </div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {lead.existing_products.map((p) => (
                  <span key={p} className="rounded-md bg-white/5 px-2 py-0.5 text-xs text-slate-400 ring-1 ring-white/10">{p}</span>
                ))}
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <div className="text-right">
                <div className="text-[11px] font-semibold uppercase text-slate-400">Predicted conversion</div>
                <div className="gradient-text font-display text-4xl font-extrabold">{pct(lead.predicted_conversion, 0)}</div>
              </div>
              <div className="flow-border rounded-xl p-4">
                <div className="text-[11px] font-semibold uppercase text-slate-400">Best-fit offer</div>
                <div className="font-display text-lg font-bold text-white">{lead.recommended_product_label}</div>
                <div className="text-sm text-slate-300">{lakh(lead.recommended_amount)} · {inr(lead.indicative_emi)}/mo · {(lead.annual_rate * 100).toFixed(1)}%</div>
              </div>
            </div>
          </div>
        </Card>
      </Reveal>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        {/* LEFT — intelligence */}
        <div className="space-y-4 xl:col-span-7">
          <Reveal>
            <Card className="p-5">
              <SectionTitle sub="Transparent factor breakdown behind the lead score.">Lead score · {lead.lead_quality_score}/100</SectionTitle>
              <div className="space-y-3">
                <ScoreBar label="Loan intent" value={comp.intent} max={40} hint={`${comp.intent}/40`} color="from-emerald-400 to-teal-400" />
                <ScoreBar label="Income confidence" value={comp.income_confidence} max={20} hint={`${comp.income_confidence}/20`} color="from-sky-400 to-cyan-400" delay={0.1} />
                <ScoreBar label="Affordability" value={comp.affordability} max={25} hint={`${comp.affordability}/25`} color="from-indigo-400 to-violet-400" delay={0.2} />
                <ScoreBar label="Profile & relationship" value={comp.profile} max={15} hint={`${comp.profile}/15`} color="from-slate-400 to-slate-500" delay={0.3} />
              </div>
            </Card>
          </Reveal>

          <Reveal delay={0.05}>
            <Card className="p-5">
              <SectionTitle sub={`Recovered from ${inc.months_observed} months of transactions.`}>
                <span className="inline-flex items-center gap-1.5"><Wallet className="h-4 w-4 text-emerald-400" /> Income estimation</span>
              </SectionTitle>
              <div className="flex flex-wrap items-end gap-6">
                <div>
                  <div className="text-[11px] uppercase text-slate-400">Verified income</div>
                  <div className="font-display text-3xl font-extrabold text-white">{inr(inc.estimated_monthly_income)}<span className="text-sm font-medium text-slate-400">/mo</span></div>
                  <div className="text-xs text-slate-400">
                    Declared {inr(inc.declared_monthly_income)}
                    {Math.abs(inc.income_uplift_pct) >= 5 && (
                      <span className={`ml-1 font-semibold ${inc.income_uplift_pct > 0 ? 'text-emerald-300' : 'text-slate-500'}`}>
                        ({inc.income_uplift_pct > 0 ? '+' : ''}{Math.round(inc.income_uplift_pct)}%)
                      </span>
                    )}
                  </div>
                </div>
                <div className="min-w-[140px] flex-1">
                  <ResponsiveContainer width="100%" height={64}>
                    <LineChart data={inc.monthly_series}>
                      <YAxis hide domain={['dataMin', 'dataMax']} />
                      <Tooltip formatter={(v: number) => inr(v)} labelFormatter={() => ''} />
                      <Line type="monotone" dataKey="income" stroke="#34d399" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2">
                <MiniKV k="Type" v={inc.income_type.replace('_', '-')} />
                <MiniKV k="Confidence" v={pct(inc.confidence)} />
                <MiniKV k="Stability" v={pct(inc.stability)} />
              </div>
              <Bullets items={inc.evidence} />
            </Card>
          </Reveal>

          <Reveal delay={0.1}>
            <Card className="p-5">
              <SectionTitle sub="FOIR head-room → eligible loan amount per product.">Repayment capacity</SectionTitle>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                <MiniKV k="Grade" v={<span className={gradeColor[aff.grade]}>{aff.grade}</span>} />
                <MiniKV k="FOIR" v={pct(aff.foir_existing)} />
                <MiniKV k="Disposable" v={inr(aff.disposable_income)} />
                <MiniKV k="Balance" v={aff.balance_trend} />
              </div>
              <div className="mt-3 overflow-hidden rounded-xl ring-1 ring-white/10">
                <table className="w-full text-sm">
                  <thead className="bg-white/5 text-[11px] uppercase text-slate-400">
                    <tr><th className="px-3 py-1.5 text-left">Product</th><th className="px-3 py-1.5 text-right">Eligible</th><th className="px-3 py-1.5 text-right">EMI</th><th className="px-3 py-1.5 text-center">OK</th></tr>
                  </thead>
                  <tbody>
                    {eligOrder.map((code) => {
                      const e = aff.eligibility[code]; if (!e) return null
                      const isReco = code === lead.recommended_product
                      return (
                        <tr key={code} className={`border-t border-white/5 ${isReco ? 'bg-emerald-400/5' : ''}`}>
                          <td className="px-3 py-1.5 text-slate-300">{PRODUCT_LABELS[code] || code}{isReco && ' ★'}</td>
                          <td className="px-3 py-1.5 text-right font-medium text-slate-200">{lakh(e.eligible_amount)}</td>
                          <td className="px-3 py-1.5 text-right text-slate-400">{inr(e.indicative_emi)}</td>
                          <td className="px-3 py-1.5 text-center">{e.eligible ? <Check className="mx-auto h-4 w-4 text-emerald-400" /> : <span className="text-slate-600">—</span>}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              <Bullets items={aff.evidence} />
            </Card>
          </Reveal>

          <Reveal delay={0.15}>
            <Card className="p-5">
              <SectionTitle sub="Per-product propensity from behavioural signals.">Buying intent</SectionTitle>
              <div className="space-y-3">
                {Object.entries(intent.product_scores).sort((a, b) => b[1] - a[1]).map(([code, s], i) => (
                  <ScoreBar key={code} label={PRODUCT_LABELS[code] || code} value={s} hint={`${Math.round(s)}`} delay={i * 0.08}
                    color={code === intent.top_product ? 'from-emerald-400 to-cyan-400' : 'from-slate-500 to-slate-600'} />
                ))}
              </div>
              {lead.why_now && (
                <div className="mt-3 rounded-xl bg-amber-500/10 p-3 ring-1 ring-amber-500/20">
                  <div className="flex items-center gap-1.5 text-xs font-bold uppercase text-amber-300">
                    <Sparkles className="h-3.5 w-3.5" /> Why now · {triggerLabel(lead.why_now.trigger)}
                  </div>
                  <div className="mt-0.5 text-sm text-amber-100/90">{lead.why_now.description}</div>
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-1.5">
                {Object.entries(intent.signals).filter(([, v]) => v).map(([k]) => (
                  <span key={k} className="rounded-md bg-emerald-400/10 px-2 py-0.5 text-xs text-emerald-300 ring-1 ring-emerald-400/20">{triggerLabel(k)}</span>
                ))}
              </div>
              <Bullets items={intent.evidence} />
            </Card>
          </Reveal>

          <Reveal delay={0.2}>
            <Card className="p-5">
              <SectionTitle sub="Evidence the analysis is built on.">Recent transactions</SectionTitle>
              <div className="max-h-64 overflow-y-auto">
                <table className="w-full text-sm">
                  <tbody>
                    {lead.recent_transactions.slice().reverse().map((t, i) => (
                      <tr key={i} className="border-b border-white/5 last:border-0">
                        <td className="py-1.5 pr-2 text-xs text-slate-500">{t.date}</td>
                        <td className="py-1.5 pr-2 text-slate-300">{t.narration}</td>
                        <td className={`py-1.5 text-right font-medium ${t.amount >= 0 ? 'text-emerald-300' : 'text-slate-300'}`}>
                          {t.amount >= 0 ? '+' : ''}{inr(t.amount)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </Reveal>
        </div>

        {/* RIGHT — copilot */}
        <div className="xl:col-span-5">
          <Card className="p-5 xl:sticky xl:top-20">
            <div className="mb-3 flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-cyan-500 text-slate-900"><Sparkles className="h-4 w-4" /></span>
              <div>
                <div className="font-display text-sm font-bold text-white">AI Copilot</div>
                <div className="text-[11px] text-slate-400">{agents ? `${agents.llm.provider}${agents.llm.model ? ' · ' + agents.llm.model : ''}` : 'loading…'}</div>
              </div>
            </div>

            <div className="mb-4 flex flex-wrap gap-1 rounded-xl bg-white/5 p-1">
              {TABS.map((t) => (
                <button key={t.k} onClick={() => setTab(t.k)}
                  className={`flex-1 rounded-lg px-2 py-1.5 text-xs font-semibold transition ${
                    tab === t.k ? 'bg-emerald-400/15 text-emerald-300 ring-1 ring-emerald-400/20' : 'text-slate-400 hover:text-slate-200'}`}>
                  {t.label}
                </button>
              ))}
            </div>

            {!agents ? <Spinner label="Running agents…" /> : (
              <AnimatePresence mode="wait">
                <motion.div key={tab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.22 }}>
                  {tab === 'brief' && (
                    <div className="space-y-3">
                      <div className="gradient-border rounded-xl p-3 text-sm font-semibold text-emerald-200">{agents.analyst.headline}</div>
                      <p className="text-sm leading-relaxed text-slate-300">{agents.analyst.summary}</p>
                      <ul className="space-y-1.5">
                        {agents.analyst.key_points.map((k, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-300"><BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />{k}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {tab === 'pitch' && pitch && (
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-1.5">
                        {meta?.channels.map((c) => (
                          <button key={c} onClick={() => changeChannel(c)}
                            className={`rounded-lg px-2.5 py-1 text-xs font-semibold ring-1 transition ${
                              channel === c ? 'bg-emerald-400/15 text-emerald-300 ring-emerald-400/30' : 'bg-white/5 text-slate-400 ring-white/10'}`}>
                            {c.replace('_', ' ')}
                          </button>
                        ))}
                      </div>
                      {pitch.subject && <div className="text-sm font-semibold text-slate-200">Subject: {pitch.subject}</div>}
                      <div className="whitespace-pre-wrap rounded-xl bg-white/5 p-3 text-sm text-slate-200 ring-1 ring-white/10">{pitch.message}</div>
                      <button onClick={() => copy(pitch.message)}
                        className="flex items-center gap-1.5 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 px-3 py-1.5 text-xs font-semibold text-slate-900 transition hover:shadow-lg hover:shadow-emerald-500/30">
                        <ClipboardCopy className="h-3.5 w-3.5" /> {copied ? 'Copied!' : 'Copy message'}
                      </button>
                    </div>
                  )}

                  {tab === 'objections' && (
                    <div className="space-y-2.5">
                      {agents.objections.objections.map((o, i) => (
                        <div key={i} className="overflow-hidden rounded-xl ring-1 ring-white/10">
                          <div className="flex items-start gap-2 bg-white/5 px-3 py-2 text-sm font-semibold text-slate-200">
                            <MessageSquare className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />{o.objection}
                          </div>
                          <div className="px-3 py-2 text-sm text-slate-400">{o.response}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {tab === 'compliance' && (
                    <div className="space-y-2.5">
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="h-4 w-4 text-emerald-400" />
                        <span className="text-sm font-semibold text-slate-200">Overall</span>
                        <StatusChip status={agents.compliance.status} />
                      </div>
                      {agents.compliance.checks.map((c, i) => (
                        <div key={i} className="rounded-lg p-2.5 ring-1 ring-white/10">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-medium text-slate-200">{c.rule}</span>
                            <StatusChip status={c.status} />
                          </div>
                          <div className="mt-0.5 text-xs text-slate-400">{c.note}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {tab === 'underwriting' && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2"><span className="text-sm font-semibold text-slate-200">Recommendation</span><StatusChip status={agents.underwriting.recommendation} /></div>
                      <p className="text-sm leading-relaxed text-slate-300">{agents.underwriting.opinion}</p>
                      <div className="grid grid-cols-2 gap-2">
                        <MiniKV k="Verified income" v={inr(agents.underwriting.assessment.verified_monthly_income)} />
                        <MiniKV k="Obligations" v={inr(agents.underwriting.assessment.existing_obligations)} />
                        <MiniKV k="FOIR (existing)" v={pct(agents.underwriting.assessment.foir_existing)} />
                        <MiniKV k="Exposure" v={lakh(agents.underwriting.assessment.recommended_exposure)} />
                      </div>
                      <div>
                        <div className="mb-1 text-xs font-bold uppercase text-slate-400">Risk flags</div>
                        <ul className="space-y-1">
                          {agents.underwriting.risk_flags.map((r, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-slate-300"><TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-400" />{r}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {tab === 'chat' && <Chat customerId={id} leadName={lead.name} />}
                </motion.div>
              </AnimatePresence>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}

function MiniKV({ k, v }: { k: string; v: ReactNode }) {
  return (
    <div className="rounded-lg bg-white/5 p-2 ring-1 ring-white/10">
      <div className="text-[10px] font-semibold uppercase text-slate-400">{k}</div>
      <div className="text-sm font-bold capitalize text-white">{v}</div>
    </div>
  )
}

function Bullets({ items }: { items: string[] }) {
  if (!items?.length) return null
  return (
    <ul className="mt-3 space-y-1 border-t border-white/5 pt-3">
      {items.map((t, i) => (
        <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
          <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-emerald-400" />{t}
        </li>
      ))}
    </ul>
  )
}
