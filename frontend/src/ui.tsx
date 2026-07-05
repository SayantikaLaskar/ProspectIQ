import { animate, motion, useInView } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { bandColor } from './format'

const EASE = [0.22, 1, 0.36, 1] as const

export function spotlightMove(e: any) {
  const el = e.currentTarget as HTMLElement
  const r = el.getBoundingClientRect()
  el.style.setProperty('--mx', `${e.clientX - r.left}px`)
  el.style.setProperty('--my', `${e.clientY - r.top}px`)
}

export function Reveal({ children, delay = 0, y = 16, className = '' }: {
  children: ReactNode; delay?: number; y?: number; className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.55, delay, ease: EASE }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function Card({ children, className = '', hover = false, glow = false }: {
  children: ReactNode; className?: string; hover?: boolean; glow?: boolean
}) {
  return (
    <div onMouseMove={spotlightMove}
      className={`spotlight rounded-2xl glass ${hover ? 'glass-hover' : ''} ${glow ? 'glow-emerald' : ''} ${className}`}>
      {children}
    </div>
  )
}

export function AnimatedNumber({ value, format = (n) => Math.round(n).toString(), className = '' }: {
  value: number; format?: (n: number) => string; className?: string
}) {
  const ref = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  const [txt, setTxt] = useState(format(0))
  useEffect(() => {
    if (!inView) return
    const controls = animate(0, value, {
      duration: 1.2, ease: EASE, onUpdate: (v) => setTxt(format(v)),
    })
    return () => controls.stop()
  }, [inView, value])
  return <span ref={ref} className={className}>{txt}</span>
}

export function Stat({ label, value, sub, icon, accent = 'text-white', delay = 0 }: {
  label: string; value: ReactNode; sub?: ReactNode; icon?: ReactNode; accent?: string; delay?: number
}) {
  return (
    <motion.div
      onMouseMove={spotlightMove}
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay, ease: EASE }}
      whileHover={{ y: -4 }}
      className="group spotlight relative overflow-hidden rounded-2xl glass glass-hover p-4"
    >
      <div className="absolute right-0 top-0 h-20 w-20 rounded-full bg-emerald-500/10 opacity-0 blur-2xl transition group-hover:opacity-100" />
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">{label}</span>
        <span className="text-slate-500 transition group-hover:text-emerald-300">{icon}</span>
      </div>
      <div className={`mt-2 font-display text-2xl font-bold leading-none ${accent}`}>{value}</div>
      {sub && <div className="mt-1.5 text-xs text-slate-400">{sub}</div>}
    </motion.div>
  )
}

export function BandPill({ band, pulse = false }: { band: string; pulse?: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${bandColor[band] || bandColor.COLD}`}>
      {pulse && band === 'HOT' && <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-rose-400" />}
      {band}
    </span>
  )
}

export function ScoreBar({ label, value, max = 100, color = 'from-emerald-400 to-teal-400', hint, delay = 0 }: {
  label: string; value: number; max?: number; color?: string; hint?: ReactNode; delay?: number
}) {
  const w = Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="text-slate-300">{label}</span>
        <span className="font-semibold text-slate-200">{hint ?? value}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${w}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.9, delay, ease: EASE }}
          className={`h-full rounded-full bg-gradient-to-r ${color}`}
        />
      </div>
    </div>
  )
}

export function SectionTitle({ children, sub }: { children: ReactNode; sub?: string }) {
  return (
    <div className="mb-4">
      <h3 className="font-display text-sm font-bold uppercase tracking-wide text-slate-200">{children}</h3>
      {sub && <p className="mt-0.5 text-xs text-slate-400">{sub}</p>}
    </div>
  )
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/15 border-t-emerald-400" />
      {label}
    </div>
  )
}

export function StatusChip({ status }: { status: string }) {
  const map: Record<string, string> = {
    PASS: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
    PROCEED: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
    REVIEW: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
    'REFER TO CREDIT': 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
    'PROCEED WITH CONDITIONS': 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
    FAIL: 'bg-rose-500/15 text-rose-300 ring-rose-500/30',
  }
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-bold ring-1 ${map[status] || 'bg-white/10 text-slate-300 ring-white/15'}`}>
      {status}
    </span>
  )
}
