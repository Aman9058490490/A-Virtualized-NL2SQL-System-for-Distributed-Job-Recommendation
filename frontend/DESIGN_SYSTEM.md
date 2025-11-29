# 🎨 Federated NL2SQL - Modern UI Design System

## Color Palette

### Light Mode
- **Primary**: Blue (#3b82f6) to Indigo (#4f46e5) gradient
- **Background**: Slate 50 (#f8fafc) to Blue 50 (#eff6ff)
- **Cards**: White with subtle shadow
- **Text**: Slate 900 (#0f172a)
- **Muted**: Slate 500 (#64748b)

### Dark Mode
- **Primary**: Blue (#60a5fa) to Indigo (#818cf8) gradient
- **Background**: Slate 950 (#020617) to Slate 900 (#0f172a)
- **Cards**: Slate 900 with border
- **Text**: Slate 50 (#f8fafc)
- **Muted**: Slate 400 (#94a3b8)

## Typography

- **Headings**: System font stack (Inter-like)
- **Body**: 14px base, 1.5 line height
- **Code**: Monospace (Consolas, Monaco)

## Components

### 1. Header
```
┌─────────────────────────────────────────────────────┐
│  [🗄️ Icon] Federated NL2SQL        [🌙 Theme Toggle]│
│  Natural Language Database Queries                  │
└─────────────────────────────────────────────────────┘
```
- Sticky header with blur backdrop
- Gradient logo text
- Theme toggle (Moon/Sun icon)

### 2. Query Input Card
```
┌─────────────────────────────────────────────────────┐
│  ✨ Natural Language Query                          │
│  Ask questions about courses and jobs              │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Find courses that teach React and jobs...    │ │
│  │                                               │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Examples: [courses that...] [compare soft...]     │
│                                                     │
│  [ ▶ Execute Query ]                               │
└─────────────────────────────────────────────────────┘
```
- Rounded corners (8px)
- Shadow on hover
- Pill-shaped example buttons
- Primary gradient button

### 3. SQL Display
```
┌─────────────────────────────────────────────────────┐
│  💻 Generated SQL Queries                          │
│  Natural query: Find courses that teach React...   │
│                                                     │
│  [Course Database] [Job Database]                  │
│  ┌───────────────────────────────────────────────┐ │
│  │ CourseDB Query              [📋 Copy]         │ │
│  │ ┌─────────────────────────────────────────┐   │ │
│  │ │ SELECT * FROM courses                   │   │ │
│  │ │ WHERE skills LIKE '%React%'             │   │ │
│  │ │ LIMIT 10;                               │   │ │
│  │ └─────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```
- Syntax highlighting (VS Code Dark Plus theme)
- Tabbed interface
- Copy button with checkmark feedback
- Bordered code blocks

### 4. Results Table
```
┌─────────────────────────────────────────────────────┐
│  📊 Query Results                                   │
│  Data fetched from databases and merged using AI   │
│                                                     │
│  [Merged (45)] [Course DB (23)] [Job DB (22)]      │
│                                                     │
│  Showing 45 of 45 rows        [CSV] [JSON]         │
│  ┌─────────────────────────────────────────────┐   │
│  │ name        │ skills      │ experience      │   │
│  ├─────────────────────────────────────────────┤   │
│  │ React Dev   │ React, JS   │ 2-4 years      │   │
│  │ Frontend    │ Vue, CSS    │ 3-5 years      │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```
- Sticky table header
- Hover row highlighting
- Export buttons
- Tab navigation with counts
- Scrollable content area

### 5. Final Answer
```
┌─────────────────────────────────────────────────────┐
│  ✨ AI-Generated Answer                             │
│                                                     │
│  💬 Based on the query results, there are 23       │
│     courses teaching React and 22 jobs requiring   │
│     React skills. The merged dataset shows strong  │
│     alignment between course offerings and job     │
│     market demands for React developers...         │
└─────────────────────────────────────────────────────┘
```
- Gradient background (primary/5 to primary/10)
- Message bubble style
- Icon indicators

## Icons (Lucide React)

All icons are from Lucide React library (NO emojis):

- **Database** - Main logo, database indicators
- **Sparkles** - AI features, query input
- **Code2** - SQL display
- **Table** - Results tables
- **Download** - Export functions
- **FileJson** - JSON export
- **Copy/Check** - Copy to clipboard
- **Send** - Submit query
- **Loader2** - Loading spinner (animated)
- **Activity** - Processing state
- **AlertCircle** - Errors
- **Moon/Sun** - Theme toggle
- **MessageSquare** - Final answer

## Animations

### Fade In
```css
@keyframes fade-in {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}
```
- Used for: Cards appearing, results loading

### Spin
```css
animation: spin 1s linear infinite;
```
- Used for: Loading indicators

### Pulse
```css
animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
```
- Used for: Activity indicators

## Responsive Breakpoints

- **Mobile**: < 640px (single column)
- **Tablet**: 640px - 1024px (2 columns where appropriate)
- **Desktop**: > 1024px (full width, max 7xl container)

## Accessibility

- ✅ ARIA labels on all interactive elements
- ✅ Keyboard navigation support
- ✅ Focus indicators
- ✅ Sufficient color contrast (WCAG AA)
- ✅ Screen reader friendly

## Modern Design Patterns

1. **Glassmorphism**
   - Backdrop blur on header/footer
   - Semi-transparent backgrounds

2. **Neumorphism** (subtle)
   - Soft shadows on cards
   - Elevated appearance

3. **Gradient Accents**
   - Blue to Indigo on primary elements
   - Text gradients on headings

4. **Micro-interactions**
   - Button hover states
   - Copy confirmation feedback
   - Smooth transitions (200-300ms)

## Example Color Usage

```tsx
// Gradient text
className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"

// Gradient button
className="bg-gradient-to-br from-blue-500 to-indigo-600"

// Glass effect
className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm"

// Card with shadow
className="rounded-lg border bg-card shadow-sm"
```

## Visual Hierarchy

1. **Level 1**: Headers, Primary actions (largest, bold)
2. **Level 2**: Section titles, Cards (medium, semi-bold)
3. **Level 3**: Body text, Data (normal weight)
4. **Level 4**: Muted text, Metadata (smaller, lighter)

---

This design system ensures a **modern, professional, and accessible** user interface with consistent styling throughout the application.
