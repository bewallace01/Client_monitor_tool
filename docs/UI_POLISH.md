# UI Polish & Design System

Complete professional UI enhancements for Client Intelligence Monitor.

## Overview

The application now features a comprehensive design system with:
- Consistent color palette and typography
- Professional animations and transitions
- Responsive design (mobile-friendly within Streamlit's limitations)
- Enhanced empty states and loading indicators
- Global search functionality
- Helpful tooltips and visual feedback

## Design System

### Color Palette

**Primary Colors:**
- Primary: `#667eea` (Purple Blue)
- Primary Dark: `#764ba2` (Deep Purple)
- Used for: Branding, primary actions, gradients

**Status Colors:**
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Amber)
- Danger: `#ef4444` (Red)
- Info: `#3b82f6` (Blue)

**Neutral Palette:**
- Gray 50-900: Complete grayscale range
- Background: `#ffffff`
- Surface: `#f9fafb`
- Border: `#e5e7eb`

**Event Type Colors:**
- Funding: `#0d6efd` (Blue)
- Acquisition: `#6610f2` (Purple)
- Leadership: `#d63384` (Pink)
- Product: `#fd7e14` (Orange)
- Partnership: `#20c997` (Teal)
- Financial: `#198754` (Green)
- Award: `#ffc107` (Yellow)
- Regulatory: `#dc3545` (Red)
- News: `#6c757d` (Gray)

### Typography

**Font Family:**
- Primary: Inter (with OpenType features)
- Fallbacks: -apple-system, BlinkMacSystemFont, sans-serif

**Font Weights:**
- Light: 300
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

**Font Features:**
- Contextual alternates (cv02, cv03, cv04, cv11)
- Letter spacing optimized for readability

## Components

### 1. Polish Module (`src/ui/polish.py`)

**Core Functions:**

```python
inject_custom_css()
# Injects comprehensive CSS styling

render_page_header(title, subtitle, icon)
# Consistent page headers with gradient text

render_empty_state(icon, title, description, action_text, action_callback)
# Beautiful empty states with optional actions

render_loading_skeleton(height, width)
# Loading placeholder animations

render_status_badge(status, text)
# Colored status indicators

get_event_type_badge(event_type)
# Event type badges with icons and colors

render_info_card(title, content, icon)
render_success_card(title, content, icon)
render_warning_card(title, content, icon)
# Colored info cards with gradients
```

**CSS Features:**

- Glass morphism effects on metric cards
- Smooth transitions and animations (0.2s timing)
- Hover effects with transforms and shadows
- Responsive breakpoints for mobile
- Print-friendly styles
- Custom scrollbars and focus states

### 2. Global Search (`src/ui/components/global_search.py`)

**Features:**
- Unified search across clients and events
- Real-time search results
- Relevance-based ranking
- Tabbed results display
- Quick navigation to results

**Search Capabilities:**
- Client search: Name, industry, description, keywords
- Event search: Title, summary, tags, event type
- Configurable result limits
- Fuzzy matching support

**Usage:**
```python
from src.ui.components import render_global_search

# In your page
render_global_search(storage)
```

## UI Enhancements

### 1. Consistent Headers

All pages now use the standardized header component:

```python
render_page_header(
    "Page Title",
    "Descriptive subtitle for context",
    "📊"  # Optional icon
)
```

### 2. Enhanced Empty States

Instead of plain text, pages now show engaging empty states:

```python
render_empty_state(
    icon="📭",
    title="No Events Found",
    description="Get started by adding clients and running your first scan."
)
```

**Features:**
- Large centered icon (4rem font size)
- Clear title and description
- Optional call-to-action button
- Fade-in animation

### 3. Loading States

```python
# Skeleton placeholder
render_loading_skeleton(height="100px", width="100%")

# Spinner with context
with st.spinner("Searching..."):
    results = perform_search()
```

### 4. Status Badges

Visual status indicators throughout the app:

```python
render_status_badge("active", "Active Client")
# Renders: Green badge with text

render_status_badge("new", "New Event")
# Renders: Blue badge with text
```

### 5. Event Type Badges

Colored badges for event types:

```python
badge_html = get_event_type_badge("funding")
st.markdown(badge_html, unsafe_allow_html=True)
# Renders: 💰 FUNDING (blue background)
```

### 6. Info Cards

Colored cards for important information:

```python
render_info_card(
    "Getting Started",
    "Add your first client to begin monitoring.",
    "ℹ️"
)

render_success_card(
    "Setup Complete",
    "Your account is ready to use!",
    "✅"
)

render_warning_card(
    "Action Required",
    "Please configure your API keys.",
    "⚠️"
)
```

## Animations & Transitions

### Fade In
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.3s ease-out; }
```

### Slide In
```css
@keyframes slideIn {
    from { transform: translateX(-10px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
.slide-in { animation: slideIn 0.3s ease-out; }
```

### Loading Skeleton
```css
.loading-skeleton {
    background: linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 50%, #e5e7eb 75%);
    background-size: 200% 100%;
    animation: loading 1.5s ease-in-out infinite;
}
```

### Hover Effects
- Buttons: `translateY(-1px)` with shadow
- Containers: `translateY(-2px)` with enhanced shadow
- Smooth 0.2s transitions

## Responsive Design

### Mobile Breakpoints
```css
@media (max-width: 768px) {
    .main-header { font-size: 2rem; }
    .subtitle { font-size: 1rem; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.5rem; }
}
```

### Print Styles
- Hide sidebar
- Hide buttons
- Optimize for paper layout

## Global Search

### Access
Navigate to: `🔍 Search` in the sidebar

### Features
1. **Unified Search Bar**
   - Search across all data
   - Minimum 2 characters
   - Real-time results

2. **Result Types**
   - Clients: Shows name, industry, description
   - Events: Shows title, client, relevance, age

3. **Result Display**
   - Tabbed interface for multiple result types
   - Color-coded relevance indicators
   - Quick "View" buttons to navigate

4. **Search Ranking**
   - Events sorted by relevance score
   - Recent results prioritized
   - Exact matches ranked higher

### Example Searches
- "funding" → Find all funding events
- "technology" → Find tech companies and related events
- "Microsoft" → Find specific company
- "acquisition" → Find acquisition news

## Tooltips

Tooltips available via helper function:

```python
from src.ui.polish import render_tooltip

tooltip_html = render_tooltip(
    "Hover me",
    "This is helpful information"
)
st.markdown(tooltip_html, unsafe_allow_html=True)
```

**Features:**
- Appears on hover
- Dark background for contrast
- Smooth fade-in transition
- Positioned above element

## Utility Classes

CSS utility classes available:

```css
.text-primary     /* Primary color text */
.text-success     /* Success color text */
.text-warning     /* Warning color text */
.text-danger      /* Danger color text */
.bg-surface       /* Surface background */
.border-primary   /* Primary border */
.fade-in          /* Fade-in animation */
.slide-in         /* Slide-in animation */
```

## Demo Mode Banner

When `DEMO_MODE=true`:
- Purple gradient banner at top
- Clear demo indication
- Exit instructions
- Visible on all pages

## Best Practices

### 1. Consistent Spacing
- Use Streamlit's native spacing (columns, dividers)
- `margin-bottom: 2rem` for sections
- `padding: 1rem` for containers

### 2. Color Usage
- Use semantic colors (success, warning, danger)
- Maintain 4.5:1 contrast ratio for accessibility
- Use gradients for premium feel

### 3. Typography
- Headers: 700 weight with gradient
- Body: 400 weight
- Labels: 500 weight, uppercase, letter-spacing

### 4. Transitions
- 0.2s for micro-interactions
- 0.3s for animations
- ease-out timing function

### 5. Shadows
- sm: Subtle elevation
- md: Medium elevation (cards)
- lg: High elevation (modals, dropdowns)

## Future Enhancements

Potential improvements:
- [ ] Keyboard shortcuts (Ctrl+K for search)
- [ ] Dark mode theme
- [ ] More animation effects
- [ ] Advanced search filters
- [ ] Search history
- [ ] Saved searches
- [ ] Export search results
- [ ] Search suggestions/autocomplete

## Browser Compatibility

Tested and optimized for:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- CSS loaded once at app startup
- Animations use GPU acceleration (transform, opacity)
- Skeleton loaders prevent layout shift
- Lazy loading for search results

## Accessibility

- WCAG 2.1 Level AA compliant colors
- Keyboard navigable
- Screen reader friendly
- Focus indicators on all interactive elements
- Alt text on all meaningful visuals

---

**Last Updated:** 2025-10-15
**Version:** 1.0.0
