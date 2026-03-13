// ============================================================
// ENUMS & CONSTANTS
// ============================================================

/** Activity type constants. */
export const ActivityType = {
  TASK: "task",
  CALL: "call",
  EMAIL: "email",
  MEETING: "meeting",
  DEADLINE: "deadline",
} as const;
export type ActivityType = (typeof ActivityType)[keyof typeof ActivityType];

/** Pipeline resource type constants. */
export const ResourceType = {
  LEAD: "lead",
  DEAL: "deal",
} as const;
export type ResourceType = (typeof ResourceType)[keyof typeof ResourceType];

/** Stage outcome constants. */
export const StageOutcome = {
  POSITIVE: "positive",
  NEGATIVE: "negative",
} as const;
export type StageOutcome = (typeof StageOutcome)[keyof typeof StageOutcome];

// ============================================================
// LINKS
// ============================================================

/** A link connecting an activity or note to a sales entity. */
export interface EntityLink {
  entity_type: string;
  entity_id: string;
  is_primary?: boolean;
}

/** Helper to create typed entity links for activities and notes. */
export const Link = {
  /** Create a link to a lead. */
  lead: (id: string, primary = true): EntityLink => ({
    entity_type: "lead",
    entity_id: id,
    is_primary: primary,
  }),
  /** Create a link to a deal. */
  deal: (id: string, primary = true): EntityLink => ({
    entity_type: "deal",
    entity_id: id,
    is_primary: primary,
  }),
  /** Create a link to a person. */
  person: (id: string, primary = false): EntityLink => ({
    entity_type: "person",
    entity_id: id,
    is_primary: primary,
  }),
  /** Create a link to an organization. */
  organization: (id: string, primary = false): EntityLink => ({
    entity_type: "organization",
    entity_id: id,
    is_primary: primary,
  }),
} as const;

// ============================================================
// PIPELINES
// ============================================================

export interface Pipeline {
  id: string;
  name: string;
  resource_type: ResourceType;
  created_at: string;
  updated_at: string;
}

export interface CreatePipelineParams {
  name: string;
  resource_type: ResourceType;
}

export interface UpdatePipelineParams {
  name?: string;
}

// ============================================================
// STAGES
// ============================================================

export interface PipelineStage {
  id: string;
  pipeline_id: string;
  name: string;
  position: number;
  is_terminal: boolean;
  outcome?: StageOutcome;
  created_at: string;
  updated_at: string;
}

export interface CreateStageParams {
  name: string;
  position: number;
  is_terminal?: boolean;
  outcome?: StageOutcome;
}

export interface UpdateStageParams {
  name?: string;
  position?: number;
  is_terminal?: boolean;
  outcome?: StageOutcome;
}

// ============================================================
// LEADS
// ============================================================

export interface Lead {
  id: string;
  label: string;
  pipeline_id: string;
  stage_id: string;
  person_id?: string;
  organization_id?: string;
  source?: string;
  owner_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateLeadParams {
  label: string;
  pipeline_id: string;
  person_id?: string;
  organization_id?: string;
  source?: string;
}

export interface UpdateLeadParams {
  label?: string;
  person_id?: string;
  organization_id?: string;
  source?: string;
}

export interface ListLeadsParams {
  pipeline_id?: string;
}

export interface ConvertLeadParams {
  deal_pipeline_id: string;
  deal_stage_id: string;
  deal_label?: string;
  value?: number;
  currency?: string;
}

// ============================================================
// DEALS
// ============================================================

export interface Deal {
  id: string;
  label: string;
  pipeline_id: string;
  stage_id: string;
  person_id?: string;
  organization_id?: string;
  value?: number;
  currency: string;
  expected_close_date?: string;
  owner_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateDealParams {
  label: string;
  pipeline_id: string;
  person_id?: string;
  organization_id?: string;
  value?: number;
  currency?: string;
  expected_close_date?: string | Date;
}

export interface UpdateDealParams {
  label?: string;
  person_id?: string;
  organization_id?: string;
  value?: number;
  currency?: string;
  expected_close_date?: string | Date;
}

export interface ListDealsParams {
  pipeline_id?: string;
}

// ============================================================
// ACTIVITIES
// ============================================================

export interface Activity {
  id: string;
  type: ActivityType;
  subject: string;
  description?: string;
  due_date?: string;
  due_time?: string;
  duration_minutes?: number;
  is_completed: boolean;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateActivityParams {
  type: ActivityType;
  subject: string;
  description?: string;
  due_date?: string | Date;
  due_time?: string;
  duration_minutes?: number;
  assigned_to_id?: string;
  links?: EntityLink[];
}

export interface UpdateActivityParams {
  subject?: string;
  description?: string;
  due_date?: string | Date;
  due_time?: string;
  duration_minutes?: number;
}

export interface ListActivitiesParams {
  lead_id?: string;
  deal_id?: string;
  type?: string;
}

// ============================================================
// NOTES
// ============================================================

export interface Note {
  id: string;
  content: string;
  author_id?: string;
  links?: EntityLink[];
  created_at: string;
  updated_at: string;
}

export interface CreateNoteParams {
  content: string;
  author_id?: string;
  links?: EntityLink[];
}

export interface UpdateNoteParams {
  content: string;
}

export interface ListNotesParams {
  lead_id?: string;
  deal_id?: string;
}

// ============================================================
// CONTACT BASES
// ============================================================

export interface ContactBase {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

// ============================================================
// PERSONS
// ============================================================

export interface Person {
  id: string;
  full_name: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  linkedin_url?: string;
  owner_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreatePersonParams {
  first_name: string;
  last_name?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
}

export interface UpdatePersonParams {
  full_name?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
}

// ============================================================
// ORGANIZATIONS
// ============================================================

export interface Organization {
  id: string;
  name: string;
  website?: string;
  linkedin_url?: string;
  owner_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateOrganizationParams {
  name: string;
  website?: string;
  linkedin_url?: string;
}

export interface UpdateOrganizationParams {
  name?: string;
  website?: string;
  linkedin_url?: string;
}
