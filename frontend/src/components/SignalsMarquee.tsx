import { motion } from 'framer-motion'

const SIGNALS = [
  'Salary credits', 'UPI inflows', 'Existing EMIs', 'Rent payments', 'SIP investments',
  'Cash deposits', 'GST inflows', 'Credit-card outflow', 'Fuel spend', 'Utility bills',
  'Balance trend', 'Dealer enquiries', 'Property tax', 'Medical spend', 'Supplier payouts',
]

function Row({ items, reverse = false, duration = 46 }: { items: string[]; reverse?: boolean; duration?: number }) {
  const row = [...items, ...items]
  return (
    <div className="overflow-hidden">
      <motion.div
        className="flex w-max gap-3"
        animate={{ x: reverse ? ['-50%', '0%'] : ['0%', '-50%'] }}
        transition={{ duration, repeat: Infinity, ease: 'linear' }}
      >
        {row.map((s, i) => (
          <span key={i} className="whitespace-nowrap rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-300">
            <span className="mr-2 font-mono text-emerald-400">/</span>{s}
          </span>
        ))}
      </motion.div>
    </div>
  )
}

export default function SignalsMarquee() {
  return (
    <div className="relative space-y-3">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-[#04060d] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-[#04060d] to-transparent" />
      <Row items={SIGNALS} duration={48} />
      <Row items={[...SIGNALS].reverse()} reverse duration={60} />
    </div>
  )
}
