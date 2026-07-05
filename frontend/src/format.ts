export const inr = (n: number) =>
  '₹' + new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Math.round(n || 0))

export const lakh = (n: number) => {
  n = n || 0
  if (Math.abs(n) >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`
  if (Math.abs(n) >= 1e5) return `₹${(n / 1e5).toFixed(1)} L`
  return inr(n)
}

export const pct = (x: number, d = 0) => `${((x || 0) * 100).toFixed(d)}%`

export const bandColor: Record<string, string> = {
  HOT: 'bg-rose-500/15 text-rose-300 ring-rose-500/30',
  WARM: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
  NURTURE: 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
  COLD: 'bg-slate-500/15 text-slate-400 ring-slate-500/30',
}

export const bandDot: Record<string, string> = {
  HOT: 'bg-rose-400', WARM: 'bg-amber-400', NURTURE: 'bg-sky-400', COLD: 'bg-slate-500',
}

export const gradeColor: Record<string, string> = {
  A: 'text-emerald-300', B: 'text-emerald-300', C: 'text-amber-300',
  D: 'text-rose-300', NA: 'text-slate-500',
}

export const triggerLabel = (t?: string) =>
  (t || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

export const empLabel = (e: string) =>
  ({ salaried: 'Salaried', self_employed: 'Self-employed', mixed: 'Mixed income' }[e] || e)
