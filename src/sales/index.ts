import type { Transport } from "../transport.js";
import type {
  Pipeline,
  CreatePipelineParams,
  UpdatePipelineParams,
  PipelineStage,
  CreateStageParams,
  UpdateStageParams,
  Lead,
  CreateLeadParams,
  UpdateLeadParams,
  ListLeadsParams,
  ConvertLeadParams,
  Deal,
  CreateDealParams,
  UpdateDealParams,
  ListDealsParams,
  Activity,
  CreateActivityParams,
  UpdateActivityParams,
  ListActivitiesParams,
  Note,
  CreateNoteParams,
  UpdateNoteParams,
  ListNotesParams,
  ContactBase,
  Person,
  CreatePersonParams,
  UpdatePersonParams,
  Organization,
  CreateOrganizationParams,
  UpdateOrganizationParams,
} from "./types.js";

type RequestFn = <T>(
  method: string,
  path: string,
  body?: unknown,
  query?: Record<string, string>,
) => Promise<T>;

type RequestVoidFn = (
  method: string,
  path: string,
  body?: unknown,
) => Promise<void>;

/** Internal type for the transport accessor needed by pagination. */
interface ClientInternals {
  _request: RequestFn;
  _requestVoid: RequestVoidFn;
  _transport: Transport;
}

/** Sales service — pipelines, stages, leads, deals, activities,
 *  notes, persons, and organizations. */
export class SalesService {
  private req: RequestFn;
  private reqVoid: RequestVoidFn;

  /** @internal — constructed by Tedo client. */
  constructor(client: ClientInternals) {
    this.req = client._request;
    this.reqVoid = client._requestVoid;
  }

  /** Format a Date or ISO string to YYYY-MM-DD for the API. */
  private formatDate(value?: string | Date): string | undefined {
    if (!value) return undefined;
    if (value instanceof Date) return value.toISOString().split("T")[0];
    return value;
  }

  // ============================================================
  // PIPELINES
  // ============================================================

  /** Create a new pipeline. */
  async createPipeline(params: CreatePipelineParams): Promise<Pipeline> {
    return this.req<Pipeline>("POST", "/sales/v1/pipelines", params);
  }

  /** List all pipelines. */
  async listPipelines(): Promise<{ pipelines: Pipeline[]; total: number }> {
    return this.req("GET", "/sales/v1/pipelines");
  }

  /** Get a pipeline by ID. */
  async getPipeline(id: string): Promise<Pipeline> {
    return this.req<Pipeline>("GET", `/sales/v1/pipelines/${id}`);
  }

  /** Update a pipeline. */
  async updatePipeline(
    id: string,
    params: UpdatePipelineParams,
  ): Promise<Pipeline> {
    return this.req<Pipeline>("PATCH", `/sales/v1/pipelines/${id}`, params);
  }

  /** Delete a pipeline. */
  async deletePipeline(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/pipelines/${id}`);
  }

  // ============================================================
  // STAGES
  // ============================================================

  /** Create a stage within a pipeline. */
  async createStage(
    pipelineId: string,
    params: CreateStageParams,
  ): Promise<PipelineStage> {
    return this.req<PipelineStage>(
      "POST",
      "/sales/v1/stages",
      { pipeline_id: pipelineId, ...params },
    );
  }

  /** List all stages in a pipeline. */
  async listStages(
    pipelineId: string,
  ): Promise<{ stages: PipelineStage[]; total: number }> {
    return this.req("GET", "/sales/v1/stages", undefined, {
      pipeline_id: pipelineId,
    });
  }

  /** Get a stage by ID. */
  async getStage(id: string): Promise<PipelineStage> {
    return this.req<PipelineStage>("GET", `/sales/v1/stages/${id}`);
  }

  /** Update a stage. */
  async updateStage(
    id: string,
    params: UpdateStageParams,
  ): Promise<PipelineStage> {
    return this.req<PipelineStage>("PATCH", `/sales/v1/stages/${id}`, params);
  }

  /** Delete a stage. */
  async deleteStage(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/stages/${id}`);
  }

  // ============================================================
  // LEADS
  // ============================================================

  /** Create a new lead. */
  async createLead(params: CreateLeadParams): Promise<Lead> {
    return this.req<Lead>("POST", "/sales/v1/leads", params);
  }

  /** List leads, optionally filtered by pipeline. */
  async listLeads(
    params?: ListLeadsParams,
  ): Promise<{ leads: Lead[]; total: number }> {
    const query: Record<string, string> = {};
    if (params?.pipeline_id) query.pipeline_id = params.pipeline_id;
    return this.req(
      "GET",
      "/sales/v1/leads",
      undefined,
      Object.keys(query).length ? query : undefined,
    );
  }

  /** Get a lead by ID. */
  async getLead(id: string): Promise<Lead> {
    return this.req<Lead>("GET", `/sales/v1/leads/${id}`);
  }

  /** Update a lead. */
  async updateLead(id: string, params: UpdateLeadParams): Promise<Lead> {
    return this.req<Lead>("PATCH", `/sales/v1/leads/${id}`, params);
  }

  /** Delete a lead. */
  async deleteLead(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/leads/${id}`);
  }

  /** Move a lead to a different stage. */
  async moveLeadStage(id: string, stageId: string): Promise<Lead> {
    return this.req<Lead>("POST", `/sales/v1/leads/${id}/move`, {
      stage_id: stageId,
    });
  }

  /** Convert a lead into a deal. */
  async convertLeadToDeal(
    id: string,
    params: ConvertLeadParams,
  ): Promise<Deal> {
    return this.req<Deal>("POST", `/sales/v1/leads/${id}/convert`, params);
  }

  // ============================================================
  // DEALS
  // ============================================================

  /** Create a new deal. */
  async createDeal(params: CreateDealParams): Promise<Deal> {
    return this.req<Deal>("POST", "/sales/v1/deals", {
      ...params,
      expected_close_date: this.formatDate(params.expected_close_date),
    });
  }

  /** List deals, optionally filtered by pipeline. */
  async listDeals(
    params?: ListDealsParams,
  ): Promise<{ deals: Deal[]; total: number }> {
    const query: Record<string, string> = {};
    if (params?.pipeline_id) query.pipeline_id = params.pipeline_id;
    return this.req(
      "GET",
      "/sales/v1/deals",
      undefined,
      Object.keys(query).length ? query : undefined,
    );
  }

  /** Get a deal by ID. */
  async getDeal(id: string): Promise<Deal> {
    return this.req<Deal>("GET", `/sales/v1/deals/${id}`);
  }

  /** Update a deal. */
  async updateDeal(id: string, params: UpdateDealParams): Promise<Deal> {
    return this.req<Deal>("PATCH", `/sales/v1/deals/${id}`, {
      ...params,
      expected_close_date: this.formatDate(params.expected_close_date),
    });
  }

  /** Delete a deal. */
  async deleteDeal(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/deals/${id}`);
  }

  /** Move a deal to a different stage. */
  async moveDealStage(id: string, stageId: string): Promise<Deal> {
    return this.req<Deal>("POST", `/sales/v1/deals/${id}/move`, {
      stage_id: stageId,
    });
  }

  // ============================================================
  // ACTIVITIES
  // ============================================================

  /** Create a new activity. */
  async createActivity(params: CreateActivityParams): Promise<Activity> {
    return this.req<Activity>("POST", "/sales/v1/activities", {
      ...params,
      due_date: this.formatDate(params.due_date),
    });
  }

  /** List activities, optionally filtered by lead, deal, or type. */
  async listActivities(
    params?: ListActivitiesParams,
  ): Promise<{ activities: Activity[]; total: number }> {
    const query: Record<string, string> = {};
    if (params?.lead_id) query.lead_id = params.lead_id;
    if (params?.deal_id) query.deal_id = params.deal_id;
    if (params?.type) query.type = params.type;
    return this.req(
      "GET",
      "/sales/v1/activities",
      undefined,
      Object.keys(query).length ? query : undefined,
    );
  }

  /** Get an activity by ID. */
  async getActivity(id: string): Promise<Activity> {
    return this.req<Activity>("GET", `/sales/v1/activities/${id}`);
  }

  /** Update an activity. */
  async updateActivity(
    id: string,
    params: UpdateActivityParams,
  ): Promise<Activity> {
    return this.req<Activity>("PATCH", `/sales/v1/activities/${id}`, {
      ...params,
      due_date: this.formatDate(params.due_date),
    });
  }

  /** Delete an activity. */
  async deleteActivity(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/activities/${id}`);
  }

  /** Mark an activity as completed or uncompleted. */
  async completeActivity(
    id: string,
    completed: boolean = true,
  ): Promise<Activity> {
    return this.req<Activity>("POST", `/sales/v1/activities/${id}/complete`, {
      completed,
    });
  }

  // ============================================================
  // NOTES
  // ============================================================

  /** Create a new note. */
  async createNote(params: CreateNoteParams): Promise<Note> {
    return this.req<Note>("POST", "/sales/v1/notes", params);
  }

  /** List notes, optionally filtered by lead or deal. */
  async listNotes(
    params?: ListNotesParams,
  ): Promise<{ notes: Note[]; total: number }> {
    const query: Record<string, string> = {};
    if (params?.lead_id) query.lead_id = params.lead_id;
    if (params?.deal_id) query.deal_id = params.deal_id;
    return this.req(
      "GET",
      "/sales/v1/notes",
      undefined,
      Object.keys(query).length ? query : undefined,
    );
  }

  /** Get a note by ID. */
  async getNote(id: string): Promise<Note> {
    return this.req<Note>("GET", `/sales/v1/notes/${id}`);
  }

  /** Update a note. */
  async updateNote(id: string, params: UpdateNoteParams): Promise<Note> {
    return this.req<Note>("PATCH", `/sales/v1/notes/${id}`, params);
  }

  /** Delete a note. */
  async deleteNote(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/notes/${id}`);
  }

  // ============================================================
  // CONTACT BASES
  // ============================================================

  /** List all contact bases. */
  async listContactBases(): Promise<{
    contact_bases: ContactBase[];
    total: number;
  }> {
    return this.req("GET", "/sales/v1/contact-bases");
  }

  /** Get a contact base by ID. */
  async getContactBase(id: string): Promise<ContactBase> {
    return this.req<ContactBase>("GET", `/sales/v1/contact-bases/${id}`);
  }

  // ============================================================
  // PERSONS
  // ============================================================

  /** Create a new person in a contact base. */
  async createPerson(
    contactBaseId: string,
    params: CreatePersonParams,
  ): Promise<Person> {
    return this.req<Person>(
      "POST",
      `/sales/v1/contact-bases/${contactBaseId}/persons`,
      params,
    );
  }

  /** List all persons in a contact base. */
  async listPersons(
    contactBaseId: string,
  ): Promise<{ persons: Person[]; total: number }> {
    return this.req(
      "GET",
      `/sales/v1/contact-bases/${contactBaseId}/persons`,
    );
  }

  /** Get a person by ID. */
  async getPerson(id: string): Promise<Person> {
    return this.req<Person>("GET", `/sales/v1/persons/${id}`);
  }

  /** Update a person. */
  async updatePerson(
    id: string,
    params: UpdatePersonParams,
  ): Promise<Person> {
    return this.req<Person>("PATCH", `/sales/v1/persons/${id}`, params);
  }

  /** Delete a person. */
  async deletePerson(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/persons/${id}`);
  }

  // ============================================================
  // ORGANIZATIONS
  // ============================================================

  /** Create a new organization in a contact base. */
  async createOrganization(
    contactBaseId: string,
    params: CreateOrganizationParams,
  ): Promise<Organization> {
    return this.req<Organization>(
      "POST",
      `/sales/v1/contact-bases/${contactBaseId}/organizations`,
      params,
    );
  }

  /** List all organizations in a contact base. */
  async listOrganizations(
    contactBaseId: string,
  ): Promise<{
    organizations: Organization[];
    total: number;
  }> {
    return this.req(
      "GET",
      `/sales/v1/contact-bases/${contactBaseId}/organizations`,
    );
  }

  /** Get an organization by ID. */
  async getOrganization(id: string): Promise<Organization> {
    return this.req<Organization>("GET", `/sales/v1/organizations/${id}`);
  }

  /** Update an organization. */
  async updateOrganization(
    id: string,
    params: UpdateOrganizationParams,
  ): Promise<Organization> {
    return this.req<Organization>(
      "PATCH",
      `/sales/v1/organizations/${id}`,
      params,
    );
  }

  /** Delete an organization. */
  async deleteOrganization(id: string): Promise<void> {
    return this.reqVoid("DELETE", `/sales/v1/organizations/${id}`);
  }
}
