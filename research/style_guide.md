# PandaDoc Style Guide

PandaDoc's visual identity is clean, modern, and professional with a warm twist. The teal-green primary combined with warm sand/coral/amethyst accents creates a distinctive feel — neither cold-corporate nor overly playful.

## 1. Color Palette

### Primary Colors
PandaDoc Green (Primary CTA & Brand)
- Default: #248567 (Teal-Emerald Green — primary buttons, links, active states)
- Dark: #136A50 (Deeper Teal — hover states)
- Pastel: #E7F0EE (Pastel Emerald — light green backgrounds)

### Accent Colors
Coral (Warm Accent)
- Default: #FF826C (Bright Coral — highlights, badges, attention)
- Pastel: #FFEAE7 (Pastel Coral — soft backgrounds)

Amethyst (Purple Accent)
- Default: #A496FF (Bright Amethyst — feature highlights, premium indicators)

Sand (Warm Neutral)
- Default: #B2A48C (Warm Sand — subtle accents)
- Pastel: #F8F5F3 (Pastel Sand — warm page backgrounds)

Gold (Premium)
- Default: #D5AD15 (Premium Gold — pricing highlights, enterprise badges)

### Neutral Colors
Black/Gray (Text & UI Elements)
- Core Black: #242424 (Near-black charcoal — headings, primary text, logo)
- Meta Gray: #888888 (Secondary text, timestamps, hints)
- Border Gray: rgba(36, 36, 36, 0.3) (Subtle borders)
- Grey-50: #C8CFD3 (Dividers, inactive elements)
- Grey-30: #F3F5F6 (Light section backgrounds)
- Grey: #E7EBED (Section backgrounds, alternating rows)

White
- White: #FFFFFF
- Translucent White: rgba(255, 255, 255, 0.8) — overlays and subtle backgrounds

### Functional Colors
- Success: #248567 (Brand Green) / Light: #E7F0EE
- Warning: #FFD54F / Light: #FFE0B2
- Error: #E44E48 / Light: #EF9A9A
- Info: #64B5F6 / Light: #90CAF9

### Brand Gradients
PandaDoc uses signature diagonal gradients (133-degree angle) for hero sections:
1. **Sand-to-Amethyst:** `linear-gradient(133deg, #F1E8E3 0%, #D6CEFF 50%, #A496FF 100%)` — warm cream to soft purple
2. **Sand-to-Emerald:** `linear-gradient(133deg, #EAE7DF 0%, #B9CDC7 65.75%, #A1C2B8 88.51%, #A1C2B8 100%)` — warm cream to sage green

**Emphasis on Translucency:** Pale and translucent colors are used extensively for overlays, card backgrounds, and subtle UI elements to create a layered, non-intrusive feel.

## 2. Typography

### Font Family
Primary Font: Graphik Alt (licensed typeface)
Fallback stack: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif
Free alternative for presentations: Inter or DM Sans

### Heading Styles
| Level | Mobile | Desktop | Weight | Color |
|-------|--------|---------|--------|-------|
| H1 | 36px | 60px | 600 (Semibold) | #242424 |
| H2 | 32px | 42px | 600 (Semibold) | #242424 |
| H3 | 24px | 32px | 600 (Semibold) | #242424 |
| H4 | 18px | 24px | 600 (Semibold) | #242424 |

### Text Colors
- Primary text: #242424 (Core Black)
- Secondary text: #888888 (Meta Gray)
- Muted text: rgba(36, 36, 36, 0.5)
- Body size: 14px–16px
- Meta/small: 12px–14px

### Font Weights
- 400 — Regular (body text)
- 600 — Semibold (headings, buttons, emphasis)
- 700 — Bold (strong emphasis, rare)

## 3. Spacing & Borders

### Border Radius Scale
- 4px — Standard (buttons, inputs)
- 8px — Medium (cards, containers)
- 16px — Large (feature cards, rounded sections)
- 50% — Circular (avatars, icon buttons)

### Borders
- Default border: 1px solid rgba(36, 36, 36, 0.1) — very subtle
- Input border: 1px solid rgba(36, 36, 36, 0.3)
- Focus border: 1px solid #248567 (brand green)
- Divider: 1px solid #C8CFD3

### Shadows
- Card shadow: 0 0 10px rgba(36, 36, 36, 0.15) — soft, diffused
- Overlay shadow: slightly stronger for floating elements

### Spacing
- Base unit: 4px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64px

## 4. Components

### Button Variants
Primary Button: Background #248567, white text, font-weight 600, border-radius 4px, min-height 50px, min-width 140px, padding 13px 18px 14px, border 2px solid #248567
- Hover: background #136A50, translateY(-2px) subtle lift effect
- Transition: 0.25s ease on all properties

Secondary Button: Background transparent, border 1px solid rgba(36, 36, 36, 0.6), text #242424
- Hover: subtle background fill, translateY(-2px)

Outline Button: Transparent with #248567 border, green text
Text Button: Text-only with #248567 color, no border or background

#### Button States Consistency
- **Active/Processing State:** Maintain a translucent white background (rgba(255, 255, 255, 0.5)) when in active/processing state, with a subtle spinner or progress animation.
- **Color Consistency:** Interactive elements related to guidance (prompts, suggestions) should use variations of the brand green (#248567 and lighter).
- **State Transitions:** All transitions use 0.25s ease. Hover includes translateY(-2px) lift effect. Smooth and subtle — no heavy animations.

### Form Elements
Input: Height 40px (standard) / 50px (large), border 1px solid rgba(36, 36, 36, 0.3), border-radius 4px
- Focus: border-color shifts to #248567 (brand green)

Toggle: Track 41px x 20px, knob 16px circle
- Off: rgba(36, 36, 36, 0.3)
- On: #248567 (brand green), knob translateX(21px)

### Cards and Containers
Card: White or translucent white background (rgba(255, 255, 255, 0.7)), border 1px solid rgba(36, 36, 36, 0.1), shadow 0 0 10px rgba(36, 36, 36, 0.15), border-radius 8px
Overlay Card: rgba(255, 255, 255, 0.85), slightly stronger shadow, for floating/modal elements

### Tables
Table: Light borders, very subtle alternating row colors (Pastel Emerald #E7F0EE for alternating rows)
Table Header: Font-weight 600, slightly lighter background
Table Row Hover: Very light highlight on hover

### Status Indicators
Active Status: Brand Green (#248567)
Inactive Status: Meta Gray (#888888)
Error Status: Error Red (#E44E48)
Warning Status: Warning Gold (#FFD54F)

### Progress Tracking
Progress Bar: Brand Green (#248567) animated fill, light gray track (#E7EBED)
Progress Steps: Connected steps — #248567 for completed, #C8CFD3 for inactive

## 5. Layout Guidelines

### Page Structure
- Container max-width: 1280px (homepage), 1200px (content pages)
- Centered with auto margins
- Generous whitespace — PandaDoc favors breathing room over density

### Responsive Breakpoints
| Breakpoint | Target |
|------------|--------|
| 600px | Small mobile |
| 768px | Tablet |
| 960px | Small desktop |
| 1200px | Full desktop |

### Grid
- 12-column grid at desktop
- Single column at mobile, 2-column at tablet
- Gutter: 24px (desktop), 16px (mobile)

### Design Philosophy
- **Generous whitespace** with structured grid layouts
- **Subtle depth** through very light shadows and borders rather than heavy elevation
- **Warm neutrals** (sand, cream pastels) rather than cold grays for backgrounds
- **Signature diagonal gradients** at 133 degrees for hero sections
- **Consistent micro-interactions** (0.25s transitions, 2px lift on hover)
- **Flat SVG icons** with solid fills matching #242424, no heavy drop shadows
- **Illustrations:** Clean, geometric/flat style

## 6. Logo
- SVG format, height 36px in navigation
- Default fill: #242424 (core black)
- Reversed variant: white (#FFFFFF) for dark backgrounds
- Always maintain clear space around the logo
