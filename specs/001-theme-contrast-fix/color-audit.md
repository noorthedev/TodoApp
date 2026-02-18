# Color Audit: Frontend Theme Contrast Fix

**Date**: 2026-02-16
**Feature**: 001-theme-contrast-fix
**Source**: frontend/src/app/globals.css

## Current Color Inventory (Light Mode Only)

### CSS Variables (`:root`)

| Variable | Color Value | Usage | Element Type |
|----------|-------------|-------|--------------|
| `--primary` | #3b82f6 | Primary actions, links, accents | Interactive |
| `--primary-hover` | #2563eb | Button hover states | Interactive |
| `--success` | #10b981 | Success indicators, checkmarks | Status |
| `--bg-site` | #f8fafc | Page background | Background |
| `--text-main` | #0f172a | Headings, body text | Text |
| `--text-muted` | #64748b | Secondary text, subtitles | Text |
| `--card-bg` | #ffffff | Card/container backgrounds | Background |

### Hardcoded Colors (Not Using Variables)

| Location | Color Value | Usage |
|----------|-------------|-------|
| `.main-card` border | #f1f5f9 | Card border |
| `.btn-outline:hover` | #eff6ff | Button hover background |
| `.features-box` | #f8fafc | Feature box background (duplicates --bg-site) |
| `.feature-list` | #475569 | Feature list text |
| `.auth-card` border | #f1f5f9 | Auth card border |
| `.auth-footer` border | #f1f5f9 | Footer border |

### Additional Colors from Button Component

From `frontend/src/components/ui/Button.tsx` (inline styles):

| Variant | Color Value | Usage |
|---------|-------------|-------|
| Primary | #0070f3 | Button background (conflicts with --primary!) |
| Secondary | #6c757d | Button background |
| Danger | #dc3545 | Button background |
| Success | #28a745 | Button background (conflicts with --success!) |
| Disabled | #ccc | Disabled button background |

## Issues Identified

### 1. Color Inconsistency
- Button component uses `#0070f3` instead of CSS variable `--primary` (#3b82f6)
- Button component uses `#28a745` for success instead of `--success` (#10b981)

### 2. Hardcoded Colors
- Multiple instances of `#f1f5f9` (border color) not using a CSS variable
- Feature box background hardcoded instead of using `--bg-site`
- Feature list text color `#475569` not using a variable

### 3. Missing Variables
- No variable for border colors
- No variable for hover states (besides primary-hover)
- No variables for button variants (secondary, danger, success)

## Recommendations

1. **Create additional CSS variables**:
   - `--border-color: #f1f5f9;`
   - `--btn-secondary: #6c757d;`
   - `--btn-danger: #dc3545;`
   - `--feature-text: #475569;`

2. **Refactor Button component** to use CSS variables instead of inline styles

3. **Replace all hardcoded colors** with CSS variables for consistency

4. **Consolidate duplicate colors** (e.g., features-box background)

## Color Usage Summary

**Total unique colors**: 14
- CSS variables: 7
- Hardcoded in CSS: 4
- Button component inline: 5 (with 2 conflicts)

**Next Steps**: Calculate contrast ratios for all colors and design dark mode palette.
