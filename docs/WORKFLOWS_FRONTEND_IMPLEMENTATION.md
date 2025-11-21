# Workflows Feature - Frontend Implementation Guide

## Overview

This document explains how the Workflows page is implemented in the frontend, how it integrates with backend APIs, and how the data flows through the application.

**Target Audience**: Frontend developers and backend developers who need to understand the frontend integration.

---

## Architecture Overview

```
┌──────────────────┐
│  User navigates  │
│  to /workflows   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Workflows.tsx   │
│  Page Component  │
└────────┬─────────┘
         │
         │ useEffect on mount
         ▼
┌──────────────────┐
│  listDocuments() │
│  API call        │
└────────┬─────────┘
         │
         │ GET /api/v1/documents?limit=50
         ▼
┌──────────────────┐
│  Backend API     │
│  Returns JSON    │
└────────┬─────────┘
         │
         │ { count, documents: [...] }
         ▼
┌──────────────────┐
│  setDocuments()  │
│  Update state    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Render workflow │
│  cards           │
└──────────────────┘
```

---

## File Structure

```
src/
├── pages/
│   └── Workflows.tsx           # Main page component
├── services/
│   └── api.ts                  # API service layer
├── components/
│   ├── Header.tsx              # Navigation header
│   └── ui/                     # shadcn/ui components
└── docs/
    ├── WORKFLOWS_FEATURE_DETAIL.md
    ├── WORKFLOWS_FRONTEND_IMPLEMENTATION.md (this file)
    └── WORKFLOWS_BACKEND_REQUIREMENTS.md
```

---

## Implementation Details

### 1. Page Component (`src/pages/Workflows.tsx`)

**Purpose**: Display list of recent workflows with actions

**Key Features**:
- Fetches workflows on page load
- Shows loading, error, and empty states
- Renders workflow cards
- Handles navigation to edit/view workflows

**Component Structure**:

```typescript
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { listDocuments, type Document } from "@/services/api";

const Workflows = () => {
  // State management
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hooks
  const { toast } = useToast();
  const navigate = useNavigate();

  // Effects
  useEffect(() => {
    // Fetch workflows on mount
  }, []);

  // Event handlers
  const handleNewWorkflow = () => { /* ... */ };
  const handleEdit = (workflowId: string) => { /* ... */ };
  const handleRun = (workflowId: string, documentType: string) => { /* ... */ };

  // Utility functions
  const getTimeAgo = (dateString: string) => { /* ... */ };
  const getWorkflowType = (documentType: string) => { /* ... */ };

  // Render
  return (
    <div>
      {/* Loading, Error, Empty, or Workflow List */}
    </div>
  );
};
```

### 2. State Management

**State Variables**:

```typescript
// Stores the list of workflow documents
const [documents, setDocuments] = useState<Document[]>([]);

// Tracks loading state during API call
const [isLoading, setIsLoading] = useState(true);

// Stores error message if API call fails
const [error, setError] = useState<string | null>(null);
```

**Why These States?**:
- `documents`: Holds the data to render
- `isLoading`: Shows spinner during fetch
- `error`: Displays error message if something goes wrong

### 3. Data Fetching

**Implementation**:

```typescript
useEffect(() => {
  const fetchWorkflows = async () => {
    try {
      setIsLoading(true);
      const response = await listDocuments(50);
      setDocuments(response.documents);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : "Failed to load workflows";
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  fetchWorkflows();
}, [toast]);
```

**Flow Breakdown**:

1. **Component Mounts** → `useEffect` runs
2. **Set Loading State** → `setIsLoading(true)` shows spinner
3. **Call API** → `listDocuments(50)` makes GET request
4. **Success** → Store documents in state, clear error
5. **Failure** → Store error message, show toast
6. **Finally** → Set loading to false (spinner disappears)

**Important Notes**:
- `useEffect` dependency array includes `toast` (from useToast hook)
- Empty dependency array would cause React warnings
- Error handling uses try/catch/finally pattern
- Loading state is set in `finally` to ensure it runs whether success or error

### 4. API Service Layer (`src/services/api.ts`)

**Function**: `listDocuments()`

```typescript
/**
 * List all documents
 *
 * @param limit - Maximum number of documents to return (default: 50)
 * @returns List of documents
 */
export const listDocuments = async (
  limit: number = 50
): Promise<{ count: number; documents: Document[] }> => {
  const response = await fetch(
    `${API_BASE}/api/v1/documents?limit=${limit}`
  );

  if (!response.ok) {
    const errorData = await response.json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || 'Failed to list documents');
  }

  return response.json();
};
```

**What This Does**:
1. Makes GET request to `/api/v1/documents?limit=50`
2. Checks if response is successful (status 200-299)
3. If error, tries to parse error message from JSON
4. If success, returns parsed JSON response
5. TypeScript ensures return type matches interface

**Type Definition**:

```typescript
export interface Document {
  id: number;
  workflow_id: string;
  title: string;
  client_name: string;
  document_type: string;
  content: string;
  created_at: string;
  updated_at: string;
  last_edited_by?: {
    id: number;
    name: string;
    email: string;
  };
}
```

### 5. Event Handlers

#### New Workflow

```typescript
const handleNewWorkflow = () => {
  navigate("/quick-proposal");
};
```

**Purpose**: Create a new workflow
**Action**: Redirect to Quick Proposal page
**User Trigger**: Click "+ New Workflow" button

#### Edit Workflow

```typescript
const handleEdit = (workflowId: string) => {
  navigate("/quick-proposal", { state: { workflowId } });
};
```

**Purpose**: Edit existing workflow
**Action**: Navigate with workflowId in state
**User Trigger**: Click "Edit" button on workflow card

**How State Passing Works**:
```typescript
// Workflows.tsx sends:
navigate("/quick-proposal", { state: { workflowId: "WF-123" } });

// QuickProposal.tsx receives:
import { useLocation } from "react-router-dom";

const location = useLocation();
const workflowId = location.state?.workflowId;

if (workflowId) {
  // Load existing workflow
  const doc = await getDocument(workflowId);
  // Populate form with existing data
}
```

#### View/Run Workflow

```typescript
const handleRun = (workflowId: string, documentType: string) => {
  if (documentType === "proposal") {
    navigate("/quick-proposal", { state: { workflowId } });
  } else {
    navigate("/upload-rfp", { state: { workflowId } });
  }
};
```

**Purpose**: View workflow results
**Action**: Navigate to appropriate page based on workflow type
**Logic**:
- `proposal` → Quick Proposal page
- `rfp_response` → Upload RFP page

### 6. Utility Functions

#### Time Ago Calculation

```typescript
const getTimeAgo = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  if (diffWeeks < 4) return `${diffWeeks} week${diffWeeks > 1 ? 's' : ''} ago`;
  return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
};
```

**Input**: ISO timestamp string (e.g., `"2024-11-18T10:30:00"`)
**Output**: Human-readable time (e.g., `"2 days ago"`)

**How It Works**:
1. Parse date string to Date object
2. Get current time
3. Calculate difference in milliseconds
4. Convert to minutes, hours, days, weeks, months
5. Return appropriate format based on magnitude

#### Workflow Type Display

```typescript
const getWorkflowType = (documentType: string) => {
  if (documentType === "rfp_response") return "RFP Response";
  return "Quick Proposal";
};
```

**Purpose**: Convert `document_type` to display-friendly label
**Mapping**:
- `"rfp_response"` → `"RFP Response"`
- `"proposal"` → `"Quick Proposal"`
- Any other → `"Quick Proposal"` (default)

### 7. Rendering Logic

#### Conditional Rendering

```typescript
{/* Loading State */}
{isLoading && (
  <div className="flex items-center justify-center py-12">
    <Loader2 className="w-8 h-8 animate-spin text-primary" />
  </div>
)}

{/* Error State */}
{error && !isLoading && (
  <Card className="p-8 text-center">
    <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
    <h3 className="text-lg font-semibold mb-2">Failed to Load Workflows</h3>
    <p className="text-muted-foreground">{error}</p>
  </Card>
)}

{/* Empty State */}
{!isLoading && !error && documents.length === 0 && (
  <Card className="p-12 text-center">
    <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
    <h3 className="text-xl font-semibold mb-2">No Workflows Yet</h3>
    <p className="text-muted-foreground mb-6">
      Get started by creating your first proposal workflow
    </p>
    <Button onClick={handleNewWorkflow}>
      <Plus className="w-4 h-4 mr-2" />
      Create First Workflow
    </Button>
  </Card>
)}

{/* Workflows List */}
{!isLoading && !error && documents.length > 0 && (
  <div className="grid gap-4">
    {documents.map((document) => (
      <WorkflowCard key={document.id} document={document} />
    ))}
  </div>
)}
```

**State Priority**:
1. **Loading** → Show spinner (highest priority)
2. **Error** → Show error message (if not loading)
3. **Empty** → Show empty state (if no documents)
4. **Success** → Show workflow cards (if documents exist)

#### Workflow Card Component

```typescript
<Card key={document.id} className="p-6 hover:shadow-md transition-shadow">
  <div className="flex items-center justify-between">
    {/* Left Section */}
    <div className="flex items-center gap-4">
      <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
        <GitBranch className="w-6 h-6 text-primary" />
      </div>
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h3 className="text-lg font-semibold">{document.title}</h3>
          <Badge variant="default">
            {getWorkflowType(document.document_type)}
          </Badge>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>{document.client_name}</span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {getTimeAgo(document.updated_at)}
          </span>
          {document.last_edited_by && (
            <>
              <span>•</span>
              <span>Edited by {document.last_edited_by.name}</span>
            </>
          )}
        </div>
      </div>
    </div>

    {/* Right Section - Actions */}
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleEdit(document.workflow_id)}
      >
        Edit
      </Button>
      <Button
        size="sm"
        onClick={() => handleRun(document.workflow_id, document.document_type)}
      >
        View
      </Button>
    </div>
  </div>
</Card>
```

**Card Layout**:
- **Icon**: GitBranch icon in colored circle
- **Title**: Workflow title (bold)
- **Badge**: Workflow type (colored badge)
- **Metadata**: Client name, time, editor (muted text)
- **Actions**: Edit and View buttons (right-aligned)

---

## Integration with Backend

### API Endpoint

**Request**:
```
GET http://localhost:8000/api/v1/documents?limit=50
```

**Headers**:
```
Accept: application/json
```

**Response** (Success - 200):
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
      "content": "# Proposal...",
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

**Response** (Error - 500):
```json
{
  "detail": "Database connection failed"
}
```

### Error Handling

**Network Errors**:
```typescript
try {
  const response = await listDocuments(50);
} catch (err) {
  // Handles:
  // - Network timeouts
  // - Connection refused
  // - DNS failures
  // - HTTP errors (404, 500, etc.)
  setError(err.message);
}
```

**API Error Messages**:
- Backend returns `{ detail: "error message" }`
- Frontend extracts and displays the message
- Falls back to `response.statusText` if no detail

---

## Data Flow Diagram

```
User Opens /workflows
         │
         ▼
  ┌─────────────┐
  │  Component  │
  │  Mounts     │
  └──────┬──────┘
         │
         │ useEffect runs
         ▼
  ┌─────────────┐
  │ isLoading = │
  │    true     │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ API Request │
  │GET /docs    │
  └──────┬──────┘
         │
         ├─── Success ───┐
         │               │
         │               ▼
         │        ┌─────────────┐
         │        │setDocuments │
         │        │  (array)    │
         │        └──────┬──────┘
         │               │
         ├─── Error ────┐│
         │              ││
         │              ▼▼
         │        ┌─────────────┐
         │        │ isLoading = │
         │        │   false     │
         │        └──────┬──────┘
         │               │
         │               ▼
         │        ┌─────────────┐
         │        │   Render    │
         │        │   Content   │
         │        └─────────────┘
         │
User Clicks Edit Button
         │
         ▼
  ┌─────────────┐
  │ navigate()  │
  │ with state  │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Quick       │
  │ Proposal    │
  │ Page        │
  └─────────────┘
```

---

## Styling and UI

### Tailwind Classes Used

**Layout**:
- `min-h-screen` - Full viewport height
- `container` - Responsive container
- `max-w-5xl mx-auto` - Centered content
- `flex items-center justify-between` - Flexbox alignment

**Spacing**:
- `px-4 py-8 md:px-6 md:py-12` - Responsive padding
- `gap-4` - Grid gap between cards
- `mb-8` - Margin bottom

**Cards**:
- `p-6` - Card padding
- `hover:shadow-md transition-shadow` - Hover effect
- `rounded-lg` - Rounded corners

**Typography**:
- `text-4xl font-bold` - Page title
- `text-lg font-semibold` - Workflow title
- `text-sm text-muted-foreground` - Metadata text

### Component Library

**shadcn/ui components**:
- `Card` - Workflow card container
- `Button` - Action buttons
- `Badge` - Workflow type badge
- `Loader2` - Loading spinner (from Lucide)

---

## Future Enhancements

### Loading State with Skeleton

Replace spinner with skeleton cards:

```typescript
{isLoading && (
  <div className="grid gap-4">
    {[1, 2, 3].map(i => (
      <Card key={i} className="p-6">
        <Skeleton className="h-12 w-12 rounded-lg" />
        <Skeleton className="h-6 w-3/4 mt-4" />
        <Skeleton className="h-4 w-1/2 mt-2" />
      </Card>
    ))}
  </div>
)}
```

### Pagination

Add pagination for large workflow lists:

```typescript
const [page, setPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);

const fetchWorkflows = async (pageNum: number) => {
  const response = await listDocuments(50, (pageNum - 1) * 50);
  // Update state
};
```

### Real-time Updates

Use React Query for automatic refetching:

```typescript
import { useQuery } from '@tanstack/react-query';

const { data, isLoading, error } = useQuery({
  queryKey: ['workflows'],
  queryFn: () => listDocuments(50),
  refetchInterval: 30000, // Refetch every 30 seconds
});
```

---

## Debugging Tips

### Common Issues

**1. Documents not loading**:
- Check browser console for errors
- Verify API_BASE URL in `api.ts`
- Test API endpoint in Postman/curl
- Check network tab in DevTools

**2. Navigation not working**:
- Verify routes in `App.tsx`
- Check if `workflowId` is passed correctly
- Inspect `location.state` in target component

**3. Time calculations wrong**:
- Verify date format from backend (ISO 8601)
- Check timezone handling
- Test with different dates

### Console Logging

Add debug logs:

```typescript
useEffect(() => {
  const fetchWorkflows = async () => {
    console.log('Fetching workflows...');
    const response = await listDocuments(50);
    console.log('Response:', response);
    console.log('Documents count:', response.documents.length);
  };
}, []);
```

---

## Testing

### Manual Testing Steps

1. **Open Workflows page** → Should show loading spinner
2. **Wait for load** → Should show workflow cards or empty state
3. **Click "+ New Workflow"** → Should navigate to Quick Proposal
4. **Click "Edit" on card** → Should navigate with workflowId
5. **Click "View" on card** → Should navigate to appropriate page
6. **Disconnect network** → Should show error message
7. **Refresh page** → Should refetch data

### Unit Test Example (Future)

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import Workflows from './Workflows';

test('displays workflows after loading', async () => {
  render(<Workflows />);

  // Loading state
  expect(screen.getByRole('progressbar')).toBeInTheDocument();

  // After load
  await waitFor(() => {
    expect(screen.getByText('Proposal for Acme Corp')).toBeInTheDocument();
  });
});
```

---

## Conclusion

The Workflows page is a straightforward list view that:
1. Fetches documents from backend on mount
2. Displays them in a card layout
3. Provides navigation to edit/view workflows
4. Handles loading, error, and empty states

The implementation follows React best practices:
- Functional components with hooks
- Proper error handling
- Conditional rendering based on state
- Separation of concerns (API layer, component layer)
- TypeScript for type safety

This serves as a solid foundation for future enhancements like filtering, search, and advanced workflow management.
