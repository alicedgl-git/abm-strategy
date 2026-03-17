# PandaDoc Style Guide

PandaDoc's visual identity emphasizes clarity, trust, and consultative selling skills.

## 1. Color Palette
### Primary Colors
Blue (Primary UI Accent)
Default: #81C784 (Softer Green)
Light: #A5D6A7 (Lighter Green)
Pale: #E8F5E9 (Very Pale Green — for subtle indicators)
Dark: #388E3C (Deeper Green — for strong success signals)

Green (Secondary — Success/Guidance)
Default: #81C784 (Softer Green)
Light: #A5D6A7 (Lighter Green)
Pale: #E8F5E9 (Very Pale Green — for subtle indicators)
Dark: #388E3C (Deeper Green — for strong success signals)

### Neutral Colors
Gray (Text & UI Elements)
Default: #616161 (Medium Gray — primary text)
Light: #9E9E9E (Light Gray — secondary text/hints)
Very Light: #E0E0E0 (Very Light Gray — for subtle dividers/backgrounds)
White/Translucent White
White: #FFFFFF
Translucent White: rgba(255, 255, 255, 0.8) — for overlays and subtle backgrounds

### Functional Colors
Success: #81C784 / Light: #C8E6C9
Warning: #FFD54F / Light: #FFE0B2
Error: #E57373 / Light: #EF9A9A
Info: #64B5F6 / Light: #90CAF9

**Emphasis on Translucency:** Pale and Translucent White colors will be used extensively for overlays, card backgrounds, and subtle UI elements to create a layered, non-intrusive feel.

## 2. Typography
### Font Family
Primary Font: Atkinson Hyperlegible (loaded from Google Fonts)
Fallback stack: system-ui, sans-serif
### Heading Styles
H1: Font weight 600, Color #616161 (Medium Gray)
H2: Font weight 600, Color #616161 (Medium Gray)
H3: Font weight 600, Color #616161 (Medium Gray)
### Text Colors
Primary text: #616161 (Medium Gray)
Secondary text: #9E9E9E (Light Gray)

## 3. Spacing & Borders
Border radius: 8px (default), 12px (cards), 50% (circular elements)
Border color: #E0E0E0 (subtle dividers)
Spacing scale: 4px base unit (4, 8, 12, 16, 24, 32, 48)

## 4. Components
### Button Variants
Primary Button (.dynapt-button-primary): Soft Blue background (#64B5F6), white text, slightly translucent background (rgba(100, 181, 246, 0.8))
Secondary Button (.dynapt-button-secondary): Light Gray background (#E0E0E0), Dark Gray text (#616161), slightly translucent background (rgba(224, 224, 224, 0.8))
Outline Button (.dynapt-button-outline): Transparent with Soft Blue border (#64B5F6)
Text Button (.dynapt-button-text): Text-only button with Soft Blue text (#64B5F6)
Icon Button (.dynapt-button-icon): Icon-only circular button, Pale Blue background (#E3F2FD), translucent (rgba(227, 242, 253, 0.7))
#### Button States Consistency
- **Active/Processing State:** Buttons should maintain a translucent white background (rgba(255, 255, 255, 0.5)) when in active/processing state, regardless of hover state, with a subtle spinner or progress animation.
- **Color Consistency:** Interactive elements related to guidance (prompts, suggestions) should use variations of the Soft Green palette (#81C784 and lighter).
- **State Transitions:** Button state transitions should be smooth and subtle, using fade and slight scale animations.

### Real-time Display Elements
Transcription Panel (.dynapt-transcript-panel): Pale Blue background (#E3F2FD), translucent (rgba(227, 242, 253, 0.6)), scrollable, clear text formatting for readability.
Prompt Card (.dynapt-prompt-card): Pale Green background (#E8F5E9), translucent (rgba(232, 245, 233, 0.7)), subtle border, clear visual hierarchy for prompt text and actions.
Knowledge Snippet (.dynapt-knowledge-snippet): Translucent White background (rgba(255, 255, 255, 0.7)), light border, concise and easily digestible format.
Sentiment Indicator (.dynapt-sentiment-indicator): Subtle icon with color variations (Green for positive, Gray for neutral, Red for negative), placed unobtrusively.

### Form Elements
Input (.dynapt-input): Light background (#F2EFE6), translucent (rgba(242, 239, 230, 0.5)), subtle border, clean style.
Textarea (.dynapt-textarea): Light background (#F2EFE6), translucent (rgba(242, 239, 230, 0.5)), subtle border, clean style.

### Authentication Components
Supabase Auth UI (.dynapt-auth):
- Container: Translucent White background (rgba(255, 255, 255, 0.9))
- Input Fields: Match .dynapt-input styling
- Buttons: Follow .dynapt-button-primary patterns
- Social Auth Buttons: Use .dynapt-button-outline with provider-specific icons
- Error Messages: Use Error status color (#E57373) with subtle fade-in animation
- Success Messages: Use Success status color (#81C784) with subtle fade-in animation

### Cards and Containers
Card (.dynapt-card): Translucent White background (rgba(255, 255, 255, 0.7)), very subtle shadow, rounded corners.
Overlay Card (.dynapt-overlay-card): Translucent White background (rgba(255, 255, 255, 0.85)), slightly stronger shadow, designed for overlays on top of call interface.
### Tables
Table (.dynapt-table): Light borders, very subtle alternating row colors (Pale Blue #E3F2FD for alternating rows, translucent rgba(227, 242, 253, 0.3)).
Table Header: Bold text, slightly lighter background (Pale Blue #E3F2FD, translucent rgba(227, 242, 253, 0.5)).
Table Row Hover: Very light highlight on hover (Pale Blue #E3F2FD, translucent rgba(227, 242, 253, 0.4)).
### Status Indicators
Status Indicator (.dynapt-status-indicator): Small, subtly animated circle with specific color, translucent background (rgba(255, 255, 255, 0.6)).
Active Status: Soft Green (#81C784)
Inactive Status: Light Gray (#9E9E9E)
Error Status: Light Red (#E57373)
### Progress Tracking
Progress Bar: Light Blue (#90CAF9) animated fill, translucent background (rgba(255, 255, 255, 0.5)).
Progress Steps: Small, connected steps with subtle completion indicators (Pale Green #E8F5E9 for completed, Light Gray #9E9E9E for inactive), translucent background (rgba(255, 255, 255, 0.5)).
