/** Clean typographic logo — a pulsing signal dot + wordmark, no boxy icon. */
export default function Wordmark({ className = '' }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <span className="relative flex h-2.5 w-2.5">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_12px_2px_rgba(52,211,153,0.6)]" />
      </span>
      <span className="font-display text-base font-bold tracking-tight text-white">
        Prospect<span className="text-emerald-400">IQ</span>
      </span>
    </span>
  )
}
