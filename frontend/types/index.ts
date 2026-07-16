export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  is_superuser?: boolean;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse extends AuthTokens {
  user?: User;
}

export interface BirthProfile {
  id: string;
  user_id: string;
  profile_name: string;
  relationship: string;
  date_of_birth: string;
  time_of_birth: string | null;
  birth_place: string | null;
  latitude: number | null;
  longitude: number | null;
  timezone: string;
  accuracy_level: string;
  notes: string | null;
  chart_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface BirthChart {
  id: string;
  profile_id: string;
  chart_type: string;
  chart_data: Record<string, unknown> | null;
  generated_at: string;
}

export interface PlanetPosition {
  name?: string;
  longitude?: number;
  house: number | null;
  sign: string | null;
  sign_degree?: number;
  degree?: number;
  nakshatra: string | null;
  nakshatra_pada?: number;
  nakshatra_lord?: string;
  dignity: string | null;
  retrograde: boolean;
  combust: boolean;
  lord?: string;
  navamsa_sign?: string | null;
  navamsa_house?: number | null;
  navamsa_degree?: number | null;
  aspects?: string[];
  conjunctions?: string[];
}

export interface ChartData {
  planets: Record<string, PlanetPosition>;
  yogas: string[];
  doshas: string[];
  dashas: string[];
  topics: string[];
}

export interface AIResponse {
  direct_answer: string;
  interpretation: string;
  supporting_factors: string[];
  conflicting_factors: string[];
  overall_confidence: number;
  references: string[];
  follow_up_questions: string[];
  language: string;
}

export interface Evidence {
  rule_id: string;
  source: string;
  conditions: string[];
  matched_conditions: string[];
  confidence: number;
  weight: number;
  match_status: string;
  supporting: string[];
  conflicting: string[];
  explanation: string;
  notes: string;
}

export interface ReasoningStep {
  step: string;
  details: string;
  evidence: string[];
}

export interface AstrologicalEntity {
  houses: number[];
  planets: string[];
  signs: string[];
  nakshatras: string[];
  yogas: string[];
  doshas: string[];
  dashas: string[];
  topics: string[];
}

export interface ReasoningResult {
  question: string;
  domain: string;
  relevant_factors: AstrologicalEntity;
  matched_rules: Evidence[];
  partially_matched_rules: Evidence[];
  unmatched_rules: Evidence[];
  supporting_evidence: Evidence[];
  conflicting_evidence: Evidence[];
  overall_confidence: number;
  reasoning_summary: string;
  reasoning_steps: ReasoningStep[];
  suggested_follow_up_topics: string[];
}

export interface ReasoningNode {
  id: string;
  label: string;
  type: string;
  children: ReasoningNode[];
  metadata: Record<string, unknown>;
}

export interface ReasoningGraph {
  root: ReasoningNode;
}

export interface RuleTrace {
  rule_id: string;
  source_book: string;
  chapter: string | null;
  verse: string | null;
  page: string | null;
  conditions: string[];
  matched_conditions: string[];
  weight: number;
  confidence: number;
  match_status: string;
  reason_included: string;
  reason_excluded: string;
}

export interface EvidenceExplanation {
  factor: string;
  why_it_matters: string;
  rule_id: string;
  source: string;
  confidence_impact: number;
}

export interface ConfidenceContribution {
  name: string;
  contribution: number;
  type: string;
}

export interface ConfidenceBreakdown {
  overall_confidence: number;
  contributors: ConfidenceContribution[];
}

export interface Limitation {
  type: string;
  description: string;
}

export interface ReferenceEntry {
  book: string;
  chapter: string | null;
  verse: string | null;
  page: string | null;
  original_language: string | null;
  translated_text: string;
}

export interface SuggestedReading {
  book: string;
  chapter: string | null;
  topic: string;
}

export interface VisualizationData {
  decision_tree: Record<string, unknown>;
  reasoning_timeline: Array<Record<string, unknown>>;
  evidence_tree: Record<string, unknown>;
  planet_influence_graph: Record<string, unknown>;
  house_influence_graph: Record<string, unknown>;
  knowledge_source_graph: Record<string, unknown>;
}

export interface ChartFactorsUsed {
  lagna: string;
  moon_sign: string;
  sun_sign: string;
  maha_dasha: string;
  antar_dasha: string;
  planets: Record<string, unknown>;
  navamsa: Record<string, unknown>;
  yogas: string[];
  doshas: string[];
}

export interface ExplainabilityReport {
  question: string;
  detected_domain: string;
  chart_factors_used: ChartFactorsUsed;
  rules_considered: string[];
  matched_rules: RuleTrace[];
  ignored_rules: RuleTrace[];
  supporting_evidence: EvidenceExplanation[];
  conflicting_evidence: EvidenceExplanation[];
  reasoning_path: ReasoningGraph | null;
  confidence_score: ConfidenceBreakdown | null;
  limitations: Limitation[];
  classical_references: ReferenceEntry[];
  suggested_reading: SuggestedReading[];
  important_notes: string[];
  visualizations: VisualizationData;
  follow_up_questions?: string[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  ai_response_json: AIResponse | null;
  reasoning_result: ReasoningResult | null;
  explainability_report: ExplainabilityReport | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  birth_profile_id: string | null;
  title: string | null;
  domain: string | null;
  summary: string | null;
  is_archived: boolean;
  is_pinned: boolean;
  is_deleted: boolean;
  confidence: number | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface Report {
  id: string;
  user_id: string;
  title: string;
  category: string;
  status: "pending" | "ready" | "failed";
  file_url: string | null;
  file_name: string | null;
  file_format: string;
  created_at: string;
  updated_at: string;
}

export interface UploadedBook {
  id: string;
  user_id: string;
  file_path: string;
  file_name: string;
  title: string | null;
  author: string | null;
  language: string | null;
  status: string;
  book_metadata: Record<string, unknown> | null;
  is_active: boolean;
  created_at: string;
}

export interface KnowledgeVersion {
  id: string;
  rule_id: string;
  version: string;
  created_at: string;
  modified_at: string;
  modified_by: string | null;
  approval_status: string;
  change_history: string | null;
  deprecated: boolean;
}

export interface KnowledgeOverview {
  books_count: number;
  versions_count: number;
  last_updated: string | null;
}

export interface Preference {
  id: string;
  user_id: string;
  preferred_language: string;
  preferred_explanation_depth: string;
  preferred_astrology_school: string;
  preferred_chart_style: string;
  citation_mode: string;
  dark_mode: boolean;
  units: string;
  notification_settings: Record<string, unknown> | null;
  timezone: string;
  country: string | null;
  theme_preference: string;
  privacy_settings: Record<string, unknown> | null;
}

export interface Feedback {
  id: string;
  user_id: string;
  rating: string;
  comment: string | null;
  created_at: string;
}

export interface ThemeSettings {
  theme: "light" | "dark" | "system";
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  message: string;
  code?: string;
}

export type SSEEvent =
  | { event: "user"; message_id: string; role: string; content: string }
  | { event: "delta"; content: string }
  | {
      event: "metadata";
      message_id: string;
      ai_response: AIResponse;
      reasoning_result: ReasoningResult;
      explainability_report: ExplainabilityReport;
      follow_up_questions: string[];
      confidence: number;
    }
  | { event: "error"; detail: string }
  | { event: "done" };

export interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  error: Error | null;
  streamingContent: string;
}

export interface SuggestedQuestion {
  id: string;
  label: string;
  question: string;
}

export interface HouseDetail {
  house: number;
  sign: string;
  lord: string;
  planets: string[];
  aspected_by: string[];
  meaning: string;
  trinity: string;
  is_kendra: boolean;
  is_upachaya: boolean;
  is_malefic: boolean;
  is_benefic: boolean;
}

export interface NakshatraDetail {
  name: string;
  pada: number;
  lord: string;
  planet: string;
  longitude: number;
  characteristics: string;
  current_influence: string;
}

export interface DashaPeriod {
  planet: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  major_themes: string[];
  relevant_planets: string[];
}

export interface YogaDetail {
  name: string;
  strength: string;
  description: string;
  conditions: string[];
  matched_conditions: string[];
  current_relevance: string;
  references: string[];
}

export interface DoshaDetail {
  name: string;
  severity: string;
  conditions: string[];
  mitigating_factors: string[];
  confidence: number;
  references: string[];
}

export interface AspectDetail {
  source: string;
  target: string;
  aspect_houses: number[];
  orb: number;
  type: string;
}

export interface TransitPosition {
  name: string;
  sign: string;
  house: number;
  longitude: number;
  nakshatra: string;
  retrograde: boolean;
}

export interface InsightHighlight {
  type: string;
  id: string;
  label: string;
  reason: string;
  strength?: string;
}

export interface StudioInsight {
  topic: string;
  highlights: InsightHighlight[];
  summary: string;
  recommendations: string[];
}

export interface BirthChartData {
  chart_type: string;
  lagna: string;
  lagna_degree: number;
  lagna_nakshatra?: string;
  moon_sign: string;
  sun_sign: string;
  maha_dasha: string;
  antar_dasha: string;
  planets: Record<string, PlanetPosition>;
  houses: Record<string, HouseDetail>;
  nakshatras: Record<string, NakshatraDetail>;
  dashas: DashaPeriod[];
  yogas: YogaDetail[];
  doshas: DoshaDetail[];
  aspects: AspectDetail[];
  transits: TransitPosition[];
  generated_at: string;
}

export interface StudioChartDetail {
  chart_id: string;
  profile_id: string;
  chart_type: string;
  lagna: string;
  lagna_degree: number;
  moon_sign: string;
  sun_sign: string;
  maha_dasha: string;
  antar_dasha: string;
  planets: Record<string, PlanetPosition>;
  houses: Record<string, HouseDetail>;
  nakshatras: Record<string, NakshatraDetail>;
  dashas: DashaPeriod[];
  yogas: YogaDetail[];
  doshas: DoshaDetail[];
  aspects: AspectDetail[];
  transits: TransitPosition[];
  visualizations: Record<string, unknown>;
  insight: StudioInsight | null;
  generated_at: string;
}
