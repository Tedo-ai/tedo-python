// Client
export { Tedo } from "./client.js";
export type { TedoOptions } from "./client.js";

// Transport
export type { Transport, TransportRequest, TransportResponse } from "./transport.js";
export { HttpTransport } from "./transport.js";

// Errors
export {
  TedoError,
  ValidationError,
  AuthenticationError,
  PermissionError,
  NotFoundError,
  RateLimitError,
  parseError,
} from "./errors.js";

// Pagination
export { Page } from "./pagination.js";

// Billing service
export { BillingService } from "./billing/index.js";

// Billing types
export type {
  Plan,
  CreatePlanParams,
  UpdatePlanParams,
  Price,
  CreatePriceParams,
  Entitlement,
  CreateEntitlementParams,
  Customer,
  CreateCustomerParams,
  UpdateCustomerParams,
  ListCustomersParams,
  Subscription,
  CreateSubscriptionParams,
  EntitlementCheck,
  CheckEntitlementParams,
  UsageRecord,
  RecordUsageParams,
  UsageSummary,
  GetUsageSummaryParams,
  PortalLink,
  CreatePortalLinkParams,
} from "./billing/types.js";

// Sales service
export { SalesService } from "./sales/index.js";

// Sales types
export type {
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
  CreateContactBaseParams,
  Person,
  CreatePersonParams,
  UpdatePersonParams,
  Organization,
  CreateOrganizationParams,
  UpdateOrganizationParams,
  EntityLink,
} from "./sales/types.js";

// Sales enums & helpers
export {
  ActivityType,
  ResourceType,
  StageOutcome,
  Link,
} from "./sales/types.js";
