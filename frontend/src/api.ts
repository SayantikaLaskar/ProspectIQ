import type { AgentBundle, Impact, LeadDetail, LeadSummary, Meta } from './types'

// In dev, BASE is '' and Vite proxies /api to the backend.
// In production, set VITE_API_URL to the deployed backend URL (e.g. https://prospectiq-api.onrender.com).
const BASE = import.meta.env.VITE_API_URL || ''

const j = async (r: Response) => {
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

export const getMeta = (): Promise<Meta> => fetch(`${BASE}/api/meta`).then(j)
export const getImpact = (): Promise<Impact> => fetch(`${BASE}/api/impact`).then(j)

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
  return fetch(`${BASE}/api/leads?${q.toString()}`).then(j)
}

export const getLead = (id: string): Promise<LeadDetail> => fetch(`${BASE}/api/leads/${id}`).then(j)

export const getAgents = (id: string, channel = 'WHATSAPP'): Promise<AgentBundle> =>
  fetch(`${BASE}/api/leads/${id}/agents?channel=${channel}`).then(j)

export const postPitch = (id: string, channel: string) =>
  fetch(`${BASE}/api/leads/${id}/pitch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ channel }),
  }).then(j)

export const postChat = (id: string, question: string, history: any[] = []) =>
  fetch(`${BASE}/api/leads/${id}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
  }).then(j)
