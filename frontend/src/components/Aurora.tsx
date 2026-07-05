const NOISE =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")"

export default function Aurora() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="grid-bg absolute inset-0 opacity-50" />
      <div className="absolute -left-32 -top-40 h-[38rem] w-[38rem] animate-aurora rounded-full bg-emerald-500/20 blur-[120px]" />
      <div className="absolute -right-40 top-1/3 h-[34rem] w-[34rem] animate-aurora-slow rounded-full bg-cyan-500/15 blur-[120px]" />
      <div className="absolute -bottom-40 left-1/3 h-[32rem] w-[32rem] animate-float-slow rounded-full bg-indigo-500/15 blur-[130px]" />
      {/* film grain */}
      <div className="absolute inset-0 opacity-[0.035] mix-blend-overlay" style={{ backgroundImage: NOISE }} />
      {/* vignette + fade */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#04060d]/30 to-[#04060d]" />
      <div className="absolute inset-0" style={{ boxShadow: 'inset 0 0 200px 60px rgba(0,0,0,0.6)' }} />
    </div>
  )
}
