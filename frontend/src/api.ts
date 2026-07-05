import type { AgentBundle, Impact, LeadDetail, LeadSummary, Meta } from './types'

// In dev, BASE is '' and Vite proxies /api to the backend.
// In production, set VITE_API_URL to the deployed backend URL.
const BASE = import.meta.env.VITE_API_URL || ''

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

// Retries transparently while a free-tier backend is waking from cold start
// (those failures surface as network/CORS errors or 502/503). Once it's up,
// the request succeeds — so the UI shows a spinner, then loads, never a hard error.
async function req(path: string, opts?: RequestInit): Promise<any> {
  const tries = 12
  let lastErr: unknown
  for (let i = 0; i < tries; i++) {
    try {
      const r = await fetch(`${BASE}${path}`, opts)
      if (r.ok) return r.json()
      if ([502, 503, 504].includes(r.status)) { lastErr = new Error(`HTTP ${r.status}`); await sleep(4000); continue }
      throw new Error(`HTTP ${r.status}`) // real 4xx — fail fast
    } catch (e) {
      lastErr = e
      if (i < tries - 1) await sleep(4000) // network/CORS (backend waking) — retry
    }
  }
  throw lastErr instanceof Error ? lastErr : new Error('Backend unavailable')
}

export const getMeta = (): Promise<Meta> => req('/api/meta')
export const getImpact = (): Promise<Impact> => req('/api/impact')

export interface LeadQuery {
  product?: string
  band?: string
  min_conv?: number
  search?: string
  limit?: number
  offset?: number
}

export const listLeads = (p: LeadQuery): Promise<{ total: number; leads: LeadSummary[] }> => {
  const q = new URLSearchParams()
  Object.entries(p).forEach(([k, v]) => {
    if (v !== undefined && v !== '' && v !== null) q.set(k, String(v))
  })
  return req(`/api/leads?${q.toString()}`)
}

export const getLead = (id: string): Promise<LeadDetail> => req(`/api/leads/${id}`)

export const getAgents = (id: string, channel = 'WHATSAPP'): Promise<AgentBundle> =>
  req(`/api/leads/${id}/agents?channel=${channel}`)

export const postPitch = (id: string, channel: string) =>
  req(`/api/leads/${id}/pitch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ channel }),
  })

export const postChat = (id: string, question: string, history: any[] = []) =>
  req(`/api/leads/${id}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
  })
