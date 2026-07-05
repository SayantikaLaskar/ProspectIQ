import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles } from 'lucide-react'
import { postChat } from '../api'

interface Msg { role: 'user' | 'assistant'; content: string }
const SUGGESTED = ["What's their real income?", 'Why this product?', 'Any risks?', 'How should I approach them?']

export default function Chat({ customerId, leadName }: { customerId: string; leadName: string }) {
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { setMessages([]) }, [customerId])
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  const send = async (q: string) => {
    if (!q.trim() || loading) return
    const history = messages.slice(-6)
    setMessages((m) => [...m, { role: 'user', content: q }])
    setInput('')
    setLoading(true)
    try {
      const r = await postChat(customerId, q, history)
      setMessages((m) => [...m, { role: 'assistant', content: r.answer }])
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: 'Sorry, I could not answer that right now.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-[460px] flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <div className="rounded-xl bg-white/5 p-4 text-sm text-slate-400 ring-1 ring-white/10">
            <div className="mb-1 flex items-center gap-1.5 font-semibold text-slate-200">
              <Sparkles className="h-4 w-4 text-emerald-400" /> Ask Prospect IQ about {leadName.split(' ')[0]}
            </div>
            Grounded in this prospect's cashflow analysis — income, eligibility, risk, why-now, and how to pitch.
          </div>
        )}
        {messages.map((m, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}
            className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-sm ${
              m.role === 'user'
                ? 'bg-gradient-to-br from-emerald-400 to-cyan-500 text-slate-900'
                : 'bg-white/5 text-slate-200 ring-1 ring-white/10'}`}>
              {m.content}
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-white/5 px-3.5 py-2 ring-1 ring-white/10">
              <span className="inline-flex gap-1">
                {[0, 1, 2].map((k) => (
                  <span key={k} className="h-1.5 w-1.5 animate-bounce rounded-full bg-emerald-400" style={{ animationDelay: `${k * 120}ms` }} />
                ))}
              </span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {messages.length === 0 && (
        <div className="my-2 flex flex-wrap gap-1.5">
          {SUGGESTED.map((q) => (
            <button key={q} onClick={() => send(q)}
              className="rounded-full bg-white/5 px-2.5 py-1 text-xs text-slate-300 ring-1 ring-white/10 transition hover:bg-emerald-400/10 hover:text-emerald-300">
              {q}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={(e) => { e.preventDefault(); send(input) }} className="mt-2 flex items-center gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about this prospect…"
          className="flex-1 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-200 outline-none focus:ring-2 focus:ring-emerald-400/40" />
        <button type="submit" disabled={loading}
          className="flex items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-cyan-500 p-2 text-slate-900 transition hover:shadow-lg hover:shadow-emerald-500/30 disabled:opacity-50">
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  )
}
