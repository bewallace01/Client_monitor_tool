# Models Test UI Page

## Overview

The **Models Test** page (`🧪 Models Test`) is an interactive Streamlit page that lets you visually verify that the data models (DTOs) work correctly without needing a database.

## Location

- **File**: `src/ui/pages/models_test.py`
- **Access**: Navigate to "🧪 Models Test" in the sidebar
- **URL**: http://localhost:8501 (then select the page)

## Features

### 1. Generate Sample Data Models

Three primary buttons to generate sample data:

#### 🏢 Generate Sample Client
- Creates a `ClientDTO` with realistic sample data
- Shows validation status
- Displays client information in a card format
- Shows UUID, priority, keywords, metadata
- Expandable JSON view
- Method testing section

#### 📰 Generate Sample Event
- Creates an `EventDTO` with realistic sample data
- Shows validation status
- Displays event in a rich card format with:
  - Event type badge
  - Relevance score indicator (🟢🟡🔴)
  - Sentiment emoji (😊😐😟)
  - Status indicator
- Interactive status change buttons:
  - "Mark as Reviewed"
  - "Mark as Actioned"
  - "Archive Event"
- Relevance testing with multiple thresholds
- Expandable JSON view

#### 💾 Generate Sample Cache
- Creates a `SearchCacheDTO` with realistic sample data
- Shows validation status
- Displays cache information:
  - API source
  - Result count
  - Cache status (Valid/Expired)
  - Query hash
  - Time until expiry
- Interactive cache management:
  - "Extend Expiry (+24h)"
  - "Refresh Cache"
- Shows cached results
- Expiry logic testing
- Expandable JSON view

### 2. Utility Functions Demo

Test utility functions in an expandable section:

- **UUID Generation**: Generate unique UUIDs on demand
- **Score Normalization**: Test relevance and sentiment score normalization
- **Time Formatting**: See how datetime values are formatted as "time ago"

### 3. Clear All Samples

Button to reset the page and clear all generated samples.

## Usage

### Basic Workflow

1. Navigate to **🧪 Models Test** in the sidebar
2. Click any of the three "Generate Sample" buttons
3. Inspect the generated data model
4. Expand sections to see raw JSON and test methods
5. Click "Clear All Samples" to start over

### Visual Inspection

The page shows:
- ✅ **Success indicators** when models validate correctly
- ❌ **Error indicators** if validation fails (with error messages)
- 📊 **Metrics** showing key values
- 📄 **JSON viewers** for raw data inspection
- 🔧 **Method testers** showing method outputs

### Interactive Features

**Client Model:**
- View all client fields in an organized card
- See keywords as a comma-separated list
- Check monitoring duration
- Inspect metadata

**Event Model:**
- Test relevance checking with different thresholds
- Change event status (reviewed → actioned → archived)
- See sentiment displayed with emojis
- View source links

**Cache Model:**
- Check if cache is expired or valid
- See time until expiry
- Extend expiry time
- Refresh cache with new data
- View all cached results

## Screenshots & Examples

### Client Display
```
Name: Acme Corporation
Industry: Technology
Domain: acmecorporation.com
Priority: HIGH

Keywords: 3
Active: Yes

Description: Acme Corporation is a leading technology company.
Account Owner: Sample Owner
Tier: Enterprise
Monitoring Since: just now
Keywords: AI, cloud, enterprise
```

### Event Display
```
┌─────────────────────────────────────────┐
│ Event Type: Funding                     │
│ Relevance: 🟢 High                      │
│ Sentiment: 😊 Positive                  │
│ Status: New                             │
├─────────────────────────────────────────┤
│ Sample Company Launches New AI Platform │
│                                         │
│ Summary: Sample Company announced...    │
│ Source: TechCrunch                      │
│ Published: just now                     │
│ Relevance Score: 85%                    │
└─────────────────────────────────────────┘
```

### Cache Display
```
API Source: newsapi
Results: 3
Status: ✅ Valid

Query: `Acme Corporation funding`
Query Hash: `ab560fa6c1d0754b...`

Cached: just now
Cache Age: 0:00:00
Expires: 2025-10-03 04:31:10
Time Until Expiry: 1 day, 0:00:00
```

## Testing Checklist

Use this page to verify:

- [x] ClientDTO creation and validation
- [x] EventDTO creation and validation
- [x] SearchCacheDTO creation and validation
- [x] UUID generation works
- [x] Validation catches errors
- [x] to_dict() serialization works
- [x] to_json() serialization works
- [x] from_dict() deserialization works
- [x] Event relevance checking works
- [x] Event status changes work
- [x] Cache expiry logic works
- [x] Cache refresh works
- [x] Utility functions work
- [x] Time formatting works
- [x] Score normalization works

## Benefits

1. **Visual Verification**: See models work without writing code
2. **No Database Required**: Test DTOs independently
3. **Interactive Testing**: Click buttons to test methods
4. **Instant Feedback**: See validation results immediately
5. **JSON Inspection**: View raw data structure
6. **Error Detection**: Catch validation issues early

## Development Notes

### Adding New Models

To add a new model to this page:

1. Import the DTO in `models_test.py`
2. Add a "Generate Sample" button
3. Create display logic for the model
4. Add expandable sections for JSON and methods
5. Update navigation if needed

### Customizing Display

The page uses Streamlit components:
- `st.columns()` for layout
- `st.metric()` for key values
- `st.expander()` for collapsible sections
- `st.json()` for JSON display
- `st.success()` / `st.error()` for validation status
- `st.code()` for method outputs

### Session State

Uses `st.session_state` to persist generated samples:
- `sample_client`: ClientDTO instance
- `sample_event`: EventDTO instance
- `sample_cache`: SearchCacheDTO instance

## Next Steps

After verifying models work:

1. ✅ Models validated → proceed to database layer
2. ✅ DTOs working → build storage implementation
3. ✅ Serialization working → integrate with API
4. ✅ Validation working → add to forms

---

**The Models Test page is your visual playground for verifying data models work correctly before integrating them into the database layer!**
