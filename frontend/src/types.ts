export interface WhyNow {
  trigger: string
  description: string
  recency_months: number
}

export interface ScoreComponents {
  intent: number
  income_confidence: number
  affordability: number
  profile: number
}

export interface LeadSummary {
  customer_id: string
  name: string
  age: number
  city: string
  city_tier: number
  employment_type: string
  credit_score: number
  declared_monthly_income: number
  estimated_monthly_income: number
  income_confidence: number
  income_type: string
  income_uplift_pct: number
  affordability_grade: string
  foir_existing: number
  predicted_conversion: number
  band: string
  lead_quality_score: number
  score_components: ScoreComponents
  recommended_product: string
  recommended_product_label: string
  recommended_amount: number
  indicative_emi: number
  annual_rate: number
  tenure_months: number
  under_review: boolean
  top_intent_score: number
  why_now: WhyNow | null
}

export interface IncomeResult {
  estimated_monthly_income: number
  income_type: string
  salary_component: number
  variable_component: number
  stability: number
  confidence: number
  months_observed: number
  declared_monthly_income: number
  income_uplift_pct: number
  monthly_series: { month: string; income: number }[]
  evidence: string[]
}

export interface Eligibility {
  eligible: boolean
  eligible_amount: number
  indicative_emi: number
  new_emi_budget: number
  foir_with_new: number
}

export interface AffordabilityResult {
  estimated_monthly_income: number
  existing_emi: number
  credit_card_outflow: number
  rent: number
  essential_spend: number
  monthly_obligations: number
  disposable_income: number
  savings_rate: number
  foir_existing: number
  balance_trend: string
  grade: string
  eligibility: Record<string, Eligibility>
  evidence: string[]
}

export interface IntentResult {
  product_scores: Record<string, number>
  top_product: string
  top_score: number
  why_now: WhyNow | null
  signals: Record<string, boolean>
  evidence: string[]
}

export interface Txn {
  date: string
  amount: number
  category: string
  channel: string
  narration: string
  balance: number
}

export interface LeadDetail extends LeadSummary {
  gender: string
  relationship_months: number
  existing_products: string[]
  disposable_income: number
  income: IncomeResult
  affordability: AffordabilityResult
  intent: IntentResult
  recent_transactions: Txn[]
}

export interface Impact {
  total_customers: number
  baseline_conversion: number
  qualify_threshold: number
  qualified_leads: number
  qualified_conversion: number
  conversion_lift_x: number | null
  hot_conversion: number
  cold_conversion: number
  model_auc: number | null
  conversion_drivers: Record<string, number>
  loan_book_opportunity: number
  product_distribution: Record<string, number>
  bands: Record<string, number>
  targeting_focus_budget: number
  targeting_comparison: Record<string, number>
  targeting_curve: { budget: number; prospect_iq: number; by_credit_score: number; by_declared_income: number; random: number }[]
  validation: {
    income_median_ape: { engine: number; declared: number }
    income_self_employed_ape: { engine: number; declared: number }
    intent_top1_accuracy: number
    intent_top2_accuracy: number
    intent_labeled: number
  }
  real_benchmark?: {
    dataset: string
    n: number
    positive_rate: number
    auc_precontact: number
    auc_with_duration: number
  }
}

export interface LLMInfo { provider: string; model: string | null; available: boolean }

export interface AgentBundle {
  analyst: { summary: string; headline: string; key_points: string[]; generated_by: LLMInfo }
  pitch: { channel: string; subject: string | null; message: string; generated_by: LLMInfo }
  objections: { objections: { objection: string; response: string }[] }
  compliance: { status: string; checks: { rule: string; status: string; note: string }[]; summary: Record<string, number> }
  underwriting: {
    assessment: Record<string, any>
    risk_flags: string[]
    evidence: string[]
    recommendation: string
    opinion: string
    generated_by: LLMInfo
  }
  llm: LLMInfo
}

export interface Meta {
  products: { code: string; label: string; annual_rate: number }[]
  bands: string[]
  channels: string[]
  llm: LLMInfo
  total_customers: number
}
