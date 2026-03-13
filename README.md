# Tedo TypeScript SDK

Official TypeScript/JavaScript SDK for the [Tedo API](https://api.tedo.ai).

## Installation

```bash
npm install tedo
# or
pnpm add tedo
```

## Quick Start

```typescript
import { Tedo } from "tedo";

const client = new Tedo("tedo_live_xxx");

// Billing: create a customer and check entitlement
const customer = await client.billing.createCustomer({
  email: "user@example.com",
  name: "Acme Corp",
});

const result = await client.billing.checkEntitlement({
  customer_id: customer.id,
  entitlement_key: "api_requests",
});

if (result.has_access) {
  console.log("Access granted");
}

// Sales: create a pipeline and add a lead
const pipeline = await client.sales.createPipeline({
  name: "Inbound",
  resource_type: "lead",
});

const lead = await client.sales.createLead({
  label: "Acme Corp",
  pipeline_id: pipeline.id,
});
```

## Pagination

List endpoints return a `Page<T>` with async iterator support:

```typescript
// Auto-paginate through all customers
const page = await client.billing.listCustomers({ limit: 20 });
for await (const customer of page) {
  console.log(customer.email);
}

// Manual pagination
const page1 = await client.billing.listCustomers({ limit: 20 });
console.log(page1.data); // Customer[]
if (page1.hasMore) {
  const page2 = await page1.nextPage();
}
```

## Error Handling

```typescript
import { NotFoundError, ValidationError, TedoError } from "tedo";

try {
  await client.billing.getCustomer("cus_xxx");
} catch (err) {
  if (err instanceof NotFoundError) {
    console.log("Customer not found");
  } else if (err instanceof ValidationError) {
    console.log("Bad request:", err.message, "field:", err.field);
  } else if (err instanceof TedoError) {
    console.log("API error:", err.code, err.status);
  }
}
```

Error classes: `ValidationError` (400), `AuthenticationError` (401), `PermissionError` (403), `NotFoundError` (404), `RateLimitError` (429).

## Custom Transport

The SDK uses a pluggable transport interface. By default it uses `HttpTransport` with native `fetch`, but you can provide your own:

```typescript
import { Tedo, Transport, TransportRequest, TransportResponse } from "tedo";

class MyTransport implements Transport {
  async request(req: TransportRequest): Promise<TransportResponse> {
    // Custom implementation
    return { status: 200, body: {} };
  }
}

const client = new Tedo({
  apiKey: "tedo_live_xxx",
  transport: new MyTransport(),
});
```

## Services

### Billing (23 methods)

| Group | Methods |
|-------|---------|
| Plans | `createPlan`, `listPlans`, `getPlan`, `updatePlan`, `deletePlan` |
| Prices | `createPrice`, `listPrices`, `archivePrice` |
| Entitlements | `createEntitlement`, `listEntitlements`, `archiveEntitlement` |
| Customers | `createCustomer`, `getCustomer`, `listCustomers`, `updateCustomer`, `deleteCustomer` |
| Subscriptions | `createSubscription`, `getSubscription`, `cancelSubscription` |
| Entitlement Check | `checkEntitlement` |
| Usage | `recordUsage`, `getUsageSummary` |
| Portal | `createPortalLink` |

### Sales (44 methods)

The sales service manages pipelines, stages, leads, deals, activities, notes, persons, organizations, and contact bases.

#### Typed constants

```typescript
import { ActivityType, ResourceType, StageOutcome } from "tedo";

ActivityType.TASK      // "task"
ActivityType.CALL      // "call"
ActivityType.EMAIL     // "email"
ActivityType.MEETING   // "meeting"
ActivityType.DEADLINE  // "deadline"

ResourceType.LEAD      // "lead"
ResourceType.DEAL      // "deal"

StageOutcome.POSITIVE  // "positive"
StageOutcome.NEGATIVE  // "negative"
```

#### Link helper

Activities and notes can be linked to sales entities using the `Link` helper:

```typescript
import { Link } from "tedo";

await client.sales.createActivity({
  type: ActivityType.CALL,
  subject: "Discovery call",
  due_date: "2024-06-01",
  links: [
    Link.lead(lead.id),          // primary link to a lead
    Link.person(person.id),      // secondary link to a person
  ],
});

// Link.deal(id, primary?)
// Link.person(id, primary?)
// Link.organization(id, primary?)
```

#### Pipelines

```typescript
// Create a pipeline for leads or deals
const pipeline = await client.sales.createPipeline({
  name: "Inbound",
  resource_type: ResourceType.LEAD,
});

const { pipelines } = await client.sales.listPipelines();
const p = await client.sales.getPipeline(pipeline.id);
await client.sales.updatePipeline(pipeline.id, { name: "New name" });
await client.sales.deletePipeline(pipeline.id);

// Stages
const stage = await client.sales.createStage(pipeline.id, {
  name: "Contacted",
  position: 1,
});

const closedStage = await client.sales.createStage(pipeline.id, {
  name: "Won",
  position: 2,
  is_terminal: true,
  outcome: StageOutcome.POSITIVE,
});
```

#### Leads

```typescript
// Create and filter leads
const lead = await client.sales.createLead({
  label: "Acme Corp",
  pipeline_id: pipeline.id,
  source: "website",
});

const { leads } = await client.sales.listLeads({ pipeline_id: pipeline.id });

// Move through stages
await client.sales.moveLeadStage(lead.id, stage.id);

// Convert to deal
const deal = await client.sales.convertLeadToDeal(lead.id, {
  deal_pipeline_id: dealPipeline.id,
  deal_stage_id: dealStage.id,
  value: 5000,
  currency: "EUR",
});
```

#### Activities

```typescript
import { ActivityType, Link } from "tedo";

const activity = await client.sales.createActivity({
  type: ActivityType.MEETING,
  subject: "Product demo",
  due_date: new Date("2024-06-15"), // accepts Date or "YYYY-MM-DD"
  due_time: "14:00",
  duration_minutes: 60,
  links: [Link.deal(deal.id)],
});

// Filter by lead, deal, or type
const { activities } = await client.sales.listActivities({
  deal_id: deal.id,
  type: ActivityType.CALL,
});

await client.sales.completeActivity(activity.id);        // mark done
await client.sales.completeActivity(activity.id, false); // mark undone
```

#### Deals

```typescript
const deal = await client.sales.createDeal({
  label: "Acme Enterprise",
  pipeline_id: dealPipeline.id,
  value: 12000,
  currency: "USD",
  expected_close_date: "2024-09-30",
});

const { deals } = await client.sales.listDeals({ pipeline_id: dealPipeline.id });
await client.sales.moveDealStage(deal.id, newStage.id);
```

#### Persons and organizations

Persons and organizations belong to a contact base:

```python
# List contact bases (each workspace has a default one)
bases = client.sales.list_contact_bases()
base_id = bases[0].id

person = client.sales.create_person(
    contact_base_id=base_id,
    first_name="Jane",
    last_name="Smith",
    email="jane@acme.com",
    phone="+1-555-0100",
)

org = client.sales.create_organization(
    contact_base_id=base_id,
    name="Acme Corp",
    website="https://acme.com",
)
```

#### Method reference

| Group | Methods |
|-------|---------|
| Pipelines | `createPipeline`, `listPipelines`, `getPipeline`, `updatePipeline`, `deletePipeline` |
| Stages | `createStage`, `listStages`, `getStage`, `updateStage`, `deleteStage` |
| Leads | `createLead`, `listLeads`, `getLead`, `updateLead`, `deleteLead`, `moveLeadStage`, `convertLeadToDeal` |
| Deals | `createDeal`, `listDeals`, `getDeal`, `updateDeal`, `deleteDeal`, `moveDealStage` |
| Activities | `createActivity`, `listActivities`, `getActivity`, `updateActivity`, `deleteActivity`, `completeActivity` |
| Notes | `createNote`, `listNotes`, `getNote`, `updateNote`, `deleteNote` |
| Contact Bases | `create_contact_base`, `list_contact_bases`, `get_contact_base` |
| Persons | `createPerson`, `listPersons`, `getPerson`, `updatePerson`, `deletePerson` |
| Organizations | `createOrganization`, `listOrganizations`, `getOrganization`, `updateOrganization`, `deleteOrganization` |

## Requirements

- Node.js >= 18 (uses native `fetch`)
- TypeScript >= 5.4 (optional)

## License

MIT
