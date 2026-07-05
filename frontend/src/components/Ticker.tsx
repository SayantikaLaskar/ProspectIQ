import { motion } from 'framer-motion'

/** Bloomberg-style seamless marquee of live headline stats. */
export default function Ticker({ items }: { items: { label: string; value: string }[] }) {
  const row = [...items, ...items]
  return (
    <div className="relative overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02] py-2">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-[#04060d] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l from-[#04060d] to-transparent" />
      <motion.div
        className="flex w-max gap-10 whitespace-nowrap px-6"
        animate={{ x: ['0%', '-50%'] }}
        transition={{ duration: 32, repeat: Infinity, ease: 'linear' }}
      >
        {row.map((it, i) => (
          <span key={i} className="flex items-center gap-2 text-xs tracking-wide">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            <span className="font-mono uppercase text-slate-500">{it.label}</span>
            <span className="tnum font-mono font-semibold text-emerald-300">{it.value}</span>
          </span>
        ))}
      </motion.div>
    </div>
  )
}
