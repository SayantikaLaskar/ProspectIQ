import { Fragment } from 'react'
import { motion } from 'framer-motion'
import { Bot, CheckCircle2, Radar, ScanLine, TrendingUp } from 'lucide-react'

const STAGES = [
  { n: '01', title: 'Ingest', sub: '12 months of transactions', icon: ScanLine },
  { n: '02', title: 'Score', sub: 'Income · Affordability · Intent', icon: Radar },
  { n: '03', title: 'Rank', sub: 'Calibrated conversion model', icon: TrendingUp },
  { n: '04', title: 'Act', sub: 'Agentic RM copilot', icon: Bot },
  { n: '05', title: 'Book', sub: 'Converted, compliant loan', icon: CheckCircle2 },
]

export default function PipelineFlow() {
  return (
    <div className="flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
      {STAGES.map((s, i) => (
        <Fragment key={s.n}>
          <motion.div
            initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.5, delay: i * 0.14, ease: [0.22, 1, 0.36, 1] }}
            className="flex-1 rounded-2xl border border-white/[0.08] bg-white/[0.04] p-5">
            <div className="font-mono text-xs text-emerald-400">{s.n}</div>
            <div className="mt-2 flex items-center gap-2">
              <s.icon className="h-5 w-5 text-emerald-300" />
              <span className="font-display font-bold text-white">{s.title}</span>
            </div>
            <div className="mt-1 text-xs text-slate-400">{s.sub}</div>
          </motion.div>
          {i < STAGES.length - 1 && (
            <motion.div
              initial={{ opacity: 0, scaleX: 0 }} whileInView={{ opacity: 1, scaleX: 1 }} viewport={{ once: true }}
              transition={{ duration: 0.3, delay: i * 0.14 + 0.12 }}
              className="mx-auto hidden h-0.5 w-8 origin-left rounded bg-gradient-to-r from-emerald-400 to-cyan-500 lg:block" />
          )}
        </Fragment>
      ))}
    </div>
  )
}
