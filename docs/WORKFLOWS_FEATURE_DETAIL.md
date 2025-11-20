# Workflows Feature - Detailed Specification

## Overview

The **Workflows** page provides a centralized view of all recent proposal and RFP processing workflows. It serves as a workflow management dashboard where users can view, edit, and re-run their previous proposals.

**Purpose**: Allow users to track, manage, and reuse their proposal workflows efficiently.

---

## Feature Description

### What is a Workflow?

In this system, a **workflow** represents a completed or in-progress proposal or RFP processing task. Each workflow:

- Has a unique `workflow_id` (e.g., `WF-QUICK-20241118103000`)
- Tracks the processing state (`created`, `analyzing`, `generating`, `ready`, etc.)
- Stores the generated content and metadata
- Can be edited, re-run, or downloaded

### Workflow Types

The system supports two main workflow types:

1. **Quick Proposal** (`document_type: "proposal"`)
   - Generated via `/quick-proposal` page
   - Creates sales proposals from client requirements
   - Faster processing (synchronous)
   - Direct markdown editing capability

2. **RFP Response** (`document_type: "rfp_response"`)
   - Generated via `/upload-rfp` page
   - Processes uploaded RFP documents
   - Multi-step background processing
   - Question extraction and answering

---

## User Experience Flow

### 1. Initial Page Load

**Scenario**: User navigates to `/workflows`

**What Happens**:
1. Page displays a loading spinner
2. Frontend calls `GET /api/v1/documents?limit=50`
3. Backend returns list of recent workflow documents
4. Page renders workflow cards with metadata

**What User Sees**:
- List of recent workflows sorted by most recently updated
- Each workflow card shows:
  - Title (e.g., "Proposal for Acme Corp")
  - Client name
  - Workflow type badge ("Quick Proposal" or "RFP Response")
  - Last updated time (e.g., "2 days ago")
  - Last editor name (if available)
  - Action buttons: "Edit" and "View"

### 2. Empty State

**Scenario**: No workflows exist yet

**What User Sees**:
- Empty state card with icon
- Message: "No Workflows Yet"
- Description: "Get started by creating your first proposal workflow"
- "Create First Workflow" button

**Action**:
- Clicking button navigates to `/quick-proposal` page

### 3. Creating New Workflow

**Scenario**: User clicks "+ New Workflow" button

**What Happens**:
- User is redirected to `/quick-proposal` page
- Can enter client details and generate a new proposal
- New workflow automatically appears in Workflows list

### 4. Editing Existing Workflow

**Scenario**: User clicks "Edit" button on a workflow card

**What Happens**:
- User is redirected to the appropriate page:
  - Quick Proposal → `/quick-proposal` with `workflowId` in state
  - RFP Response → `/upload-rfp` with `workflowId` in state
- Page loads existing workflow data
- User can edit and save changes

**Expected Behavior** (to be implemented):
- Quick Proposal page should detect `workflowId` in navigation state
- Load existing proposal content via `GET /api/v1/documents/{workflowId}`
- Display in edit mode by default
- Save button updates the existing document

### 5. Viewing Workflow Results

**Scenario**: User clicks "View" button on a workflow card

**What Happens**:
- User is redirected to the page where workflow was created
- Workflow loads in read-only/view mode
- User can see the generated content
- Option to download or edit

### 6. Time Calculations

**Workflow Recency Display**:
- Just now (< 1 minute)
- X minutes ago (< 1 hour)
- X hours ago (< 24 hours)
- X days ago (< 7 days)
- X weeks ago (< 4 weeks)
- X months ago (≥ 4 weeks)

---

## Data Model

### Workflow Document Structure

```typescript
interface Document {
  id: number;                    // Database ID
  workflow_id: string;           // Unique workflow identifier
  title: string;                 // Display title
  client_name: string;           // Client company name
  document_type: string;         // "proposal" or "rfp_response"
  content: string;               // Markdown content
  created_at: string;            // ISO timestamp
  updated_at: string;            // ISO timestamp
  last_edited_by?: {             // Optional editor info
    id: number;
    name: string;
    email: string;
  };
}
```

### API Response Example

```json
{
  "count": 2,
  "documents": [
    {
      "id": 1,
      "workflow_id": "WF-QUICK-20241118103000",
      "title": "Proposal for Acme Corp",
      "client_name": "Acme Corp",
      "document_type": "proposal",
      "content": "# Proposal for Acme Corp\n\n...",
      "created_at": "2024-11-18T10:30:00",
      "updated_at": "2024-11-18T10:35:00",
      "last_edited_by": {
        "id": 1,
        "name": "Sales Rep",
        "email": "sales@company.com"
      }
    },
    {
      "id": 2,
      "workflow_id": "WF-RFP-20241120120000",
      "title": "RFP Response for TechCo",
      "client_name": "TechCo",
      "document_type": "rfp_response",
      "content": "# RFP Response...",
      "created_at": "2024-11-20T12:00:00",
      "updated_at": "2024-11-20T12:15:00"
    }
  ]
}
```

---

## UI Components

### Page Layout

```
┌─────────────────────────────────────────────────────┐
│ Header Navigation                                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Workflows                          [+ New Workflow] │
│  Manage and review your recent proposal workflows   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ [Icon] Proposal for Acme Corp   [Quick Pro] │   │
│  │        Acme Corp • 2 days ago               │   │
│  │                         [Edit]    [View]    │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ [Icon] RFP Response for TechCo [RFP Resp]   │   │
│  │        TechCo • 1 week ago                  │   │
│  │                         [Edit]    [View]    │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Component Breakdown

**Workflow Card**:
- Left section:
  - Icon (GitBranch)
  - Title (bold)
  - Type badge
  - Metadata row (client, time, editor)
- Right section:
  - Edit button (outline variant)
  - View button (primary variant)

**States**:
1. **Loading**: Spinner centered on page
2. **Empty**: Card with icon, message, CTA button
3. **Error**: Alert card with error message
4. **Success**: Grid of workflow cards

---

## User Interactions

### Button Actions

| Button | Location | Action | Result |
|--------|----------|--------|--------|
| + New Workflow | Header | `navigate('/quick-proposal')` | Opens Quick Proposal page |
| Edit | Card | `navigate('/quick-proposal', { state: { workflowId } })` | Opens workflow in edit mode |
| View | Card | `navigate(page, { state: { workflowId } })` | Opens workflow in view mode |
| Create First Workflow | Empty state | `navigate('/quick-proposal')` | Opens Quick Proposal page |

### Navigation Patterns

**From Workflows Page**:
- → Quick Proposal (new or edit existing proposal)
- → Upload RFP (view existing RFP response)

**To Workflows Page**:
- ← Header navigation
- ← Direct URL `/workflows`
- ← After completing a workflow (optional)

---

## Implementation Details

### State Management

```typescript
const [documents, setDocuments] = useState<Document[]>([]);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

### Data Fetching

```typescript
useEffect(() => {
  const fetchWorkflows = async () => {
    try {
      setIsLoading(true);
      const response = await listDocuments(50);
      setDocuments(response.documents);
    } catch (err) {
      setError(err.message);
      toast({ title: "Error", description: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  fetchWorkflows();
}, []);
```

### Time Display Logic

```typescript
const getTimeAgo = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();

  // Calculate minutes, hours, days, weeks, months
  // Return formatted string
};
```

---

## Future Enhancements

### Phase 2 Features (Not Yet Implemented)

1. **Filtering and Search**
   - Filter by workflow type (Quick Proposal / RFP Response)
   - Filter by client name
   - Search by title or content
   - Date range filtering

2. **Sorting Options**
   - Sort by date (newest/oldest)
   - Sort by client name (A-Z)
   - Sort by workflow type

3. **Bulk Actions**
   - Select multiple workflows
   - Batch delete
   - Batch export

4. **Status Indicators**
   - Show workflow state (draft, ready, submitted)
   - Visual progress indicator
   - Error states

5. **Advanced Actions**
   - Duplicate workflow
   - Archive workflow
   - Share workflow
   - Export as PDF/DOCX directly from list

6. **Analytics**
   - Total workflows created
   - Success rate
   - Average completion time
   - Most common clients/industries

---

## Technical Considerations

### Performance

- **Pagination**: Currently loads 50 most recent workflows
  - Future: Implement infinite scroll or pagination
  - Backend should support `offset` and `limit` parameters

- **Caching**: Consider caching workflow list
  - Use React Query for automatic caching
  - Invalidate cache on new workflow creation

### Error Handling

- Network errors → Show error state with retry option
- Empty response → Show empty state
- Malformed data → Log error, show fallback UI

### Accessibility

- Keyboard navigation for workflow cards
- ARIA labels for action buttons
- Focus management when navigating back from detail pages
- Screen reader announcements for loading/error states

### Responsive Design

- Mobile: Stack workflow cards vertically
- Tablet: 2-column grid
- Desktop: Single column with full metadata
- Touch targets: Minimum 44x44px for buttons

---

## Testing Scenarios

### Manual Testing Checklist

1. **Initial Load**
   - [ ] Page shows loading spinner
   - [ ] Workflows load and display correctly
   - [ ] No console errors

2. **Empty State**
   - [ ] Shows when no workflows exist
   - [ ] "Create First Workflow" button works
   - [ ] Navigates to Quick Proposal page

3. **Workflow List**
   - [ ] Shows all workflows from API
   - [ ] Time calculations are accurate
   - [ ] Client names display correctly
   - [ ] Workflow type badges show correct labels

4. **Actions**
   - [ ] "New Workflow" button navigates correctly
   - [ ] "Edit" button passes workflowId to target page
   - [ ] "View" button navigates to correct page based on type

5. **Error Handling**
   - [ ] Network error shows error state
   - [ ] Toast notification appears on error
   - [ ] Page doesn't crash on malformed data

6. **Responsive**
   - [ ] Mobile layout works correctly
   - [ ] Desktop layout shows all information
   - [ ] Buttons are touchable on mobile

---

## Dependencies

### Frontend Libraries
- React (hooks: useState, useEffect)
- React Router (useNavigate)
- Lucide React (icons)
- shadcn/ui components (Card, Button, Badge)
- Toast notifications

### Backend APIs
- `GET /api/v1/documents?limit={n}` - List workflows

### Future Dependencies
- React Query (for caching and background refetch)
- Date-fns (for more advanced time formatting)

---

## Conclusion

The Workflows page serves as a **workflow management dashboard** that gives users visibility into their proposal generation history. The current implementation is a "Quick Win" that leverages existing backend APIs to display recent workflows without requiring new backend infrastructure.

The design is intentionally simple and extensible, allowing for future enhancements like filtering, search, and advanced analytics while providing immediate value to users today.
