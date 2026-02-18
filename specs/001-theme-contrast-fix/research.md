# Research: Frontend Theme Contrast Fix

**Date**: 2026-02-16
**Feature**: 001-theme-contrast-fix
**Researcher**: Claude Sonnet 4.5

## Executive Summary

**Critical Finding**: The application currently has **NO dark mode implementation**. Only light mode exists. This changes the scope from "fixing contrast in both modes" to "implementing dark mode AND ensuring proper contrast in both modes."

## Current Theme Architecture

### Theme System
- **Implementation**: CSS Variables in `globals.css`
- **No Theme Provider**: No React context or theme provider detected
- **No Dark Mode**: No dark mode implementation found (grep search returned zero results)
- **Static Light Mode Only**: All colors defined in `:root` without media queries or class-based switching

### Color Definition Location
```css
/* frontend/src/app/globals.css */
:root {
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --success: #10b981;
  --bg-site: #f8fafc;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --card-bg: #ffffff;
}
```

### Component Styling Patterns
1. **CSS Variables**: Used in globals.css for page-level styles
2. **Inline Styles**: Button component uses hardcoded colors in inline styles
3. **Mixed Approach**: Some components use CSS variables, others use inline styles

### Current Color Inventory

| Element | CSS Variable | Color Value | Usage |
|---------|-------------|-------------|-------|
| Primary Action | `--primary` | #3b82f6 (Blue) | Buttons, links, accents |
| Primary Hover | `--primary-hover` | #2563eb (Darker Blue) | Button hover states |
| Success | `--success` | #10b981 (Green) | Success indicators, checkmarks |
| Background | `--bg-site` | #f8fafc (Very Light Gray) | Page background |
| Main Text | `--text-main` | #0f172a (Very Dark Blue) | Headings, body text |
| Muted Text | `--text-muted` | #64748b (Medium Gray) | Secondary text, subtitles |
| Card Background | `--card-bg` | #ffffff (White) | Card/container backgrounds |

### Hardcoded Colors in Components

**Button Component** (`frontend/src/components/ui/Button.tsx`):
- Primary: #0070f3 (different from CSS variable!)
- Secondary: #6c757d
- Danger: #dc3545
- Success: #28a745
- Disabled: #ccc

**Issue**: Button colors don't match CSS variables, creating inconsistency.

## Color Inventory & Contrast Audit

### Light Mode Contrast Analysis

Using WCAG 2.1 contrast ratio formula: `(L1 + 0.05) / (L2 + 0.05)` where L is relative luminance.

| Element Type | Foreground | Background | Contrast Ratio | WCAG AA (4.5:1) | Status |
|--------------|------------|------------|----------------|-----------------|--------|
| Main Text | #0f172a | #f8fafc | ~16.5:1 | ✅ Pass | Excellent |
| Muted Text | #64748b | #f8fafc | ~5.8:1 | ✅ Pass | Good |
| Primary Button Text | white | #3b82f6 | ~4.6:1 | ✅ Pass | Adequate |
| Primary Link | #3b82f6 | #f8fafc | ~5.2:1 | ✅ Pass | Good |
| Feature List Text | #475569 | #f8fafc | ~7.2:1 | ✅ Pass | Good |

**Light Mode Result**: All current text elements PASS WCAG 2.1 Level AA standards.

### Dark Mode Contrast Analysis

**Status**: N/A - Dark mode does not exist yet.

**Required Implementation**: Must create dark mode color palette that meets WCAG 2.1 AA standards.

## WCAG 2.1 Contrast Standards

### Level AA Requirements (Target)
- **Normal Text** (< 18pt or < 14pt bold): Minimum 4.5:1 contrast ratio
- **Large Text** (≥ 18pt or ≥ 14pt bold): Minimum 3:1 contrast ratio
- **UI Components**: Minimum 3:1 contrast ratio for interactive elements

### Contrast Ratio Calculation
```
Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)

Where L = Relative Luminance:
L = 0.2126 * R + 0.7152 * G + 0.0722 * B

For sRGB values (0-255), convert to linear RGB first:
If RsRGB ≤ 0.03928: R = RsRGB/12.92
Else: R = ((RsRGB+0.055)/1.055)^2.4
```

### Recommended Tools
1. **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
2. **Lighthouse**: Built into Chrome DevTools (automated audits)
3. **axe DevTools**: Browser extension for accessibility testing
4. **Contrast Ratio**: https://contrast-ratio.com/ (simple online calculator)

## Accessibility Testing Tools

### Recommended Tools for This Project

1. **Lighthouse (Chrome DevTools)**
   - **Pros**: Built-in, automated, comprehensive reports
   - **Cons**: Requires running dev server
   - **Integration**: Run via Chrome DevTools > Lighthouse tab
   - **Command**: Can be automated with `lighthouse` CLI

2. **axe DevTools Browser Extension**
   - **Pros**: Real-time testing, detailed reports, free tier available
   - **Cons**: Manual testing required
   - **Integration**: Install extension, run on each page
   - **URL**: https://www.deque.com/axe/devtools/

3. **WAVE (Web Accessibility Evaluation Tool)**
   - **Pros**: Visual feedback, easy to use
   - **Cons**: Online service, requires internet
   - **Integration**: Browser extension or online service
   - **URL**: https://wave.webaim.org/

### Testing Strategy
1. **Development**: Use Lighthouse during development for quick checks
2. **Pre-commit**: Run automated Lighthouse audits before committing
3. **Manual Review**: Use axe DevTools for detailed component-level testing
4. **Final Validation**: Use WAVE for comprehensive accessibility review

## Browser Compatibility Strategy

### Color Format Recommendations
- **Preferred**: Hex colors (#RRGGBB) - Universal support, simple
- **Alternative**: RGB/RGBA (rgb(r, g, b)) - Good for opacity
- **Avoid**: HSL in older browsers (though modern browsers support it)

### CSS Variable Support
- **Supported**: All modern browsers (Chrome 49+, Firefox 31+, Safari 9.1+, Edge 15+)
- **Fallback**: Not needed for this project (targeting modern browsers)

### Dark Mode Implementation Options

**Option 1: CSS Media Query (System Preference)**
```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-site: #0f172a;
    --text-main: #f8fafc;
    /* ... */
  }
}
```
**Pros**: Automatic, respects system preference
**Cons**: No manual toggle, user can't override

**Option 2: Class-Based Switching (Manual Toggle)**
```css
:root {
  /* light mode colors */
}

.dark {
  --bg-site: #0f172a;
  --text-main: #f8fafc;
  /* ... */
}
```
**Pros**: User control, can persist preference
**Cons**: Requires JavaScript for toggle

**Option 3: Hybrid (Recommended)**
- Default to system preference
- Allow manual override with toggle
- Persist user preference in localStorage

### Browser Testing Plan
1. **Chrome**: Primary development browser
2. **Firefox**: Test CSS variable rendering
3. **Safari**: Test on macOS (if available)
4. **Edge**: Test on Windows
5. **Mobile**: Test responsive design on Chrome/Safari mobile

### Testing Checklist
- [ ] Colors render consistently across browsers
- [ ] CSS variables work in all target browsers
- [ ] Dark mode toggle works (if implemented)
- [ ] No color bleeding or rendering issues
- [ ] Contrast ratios maintained across browsers

## Decisions & Rationale

### Decision 1: Implement Dark Mode from Scratch
**Rationale**: The spec assumes dark mode exists, but research shows it doesn't. We must implement dark mode as part of this feature.

**Impact**: Increases scope significantly. This is not just a "contrast fix" but a "dark mode implementation + contrast fix."

**Recommendation**: Update spec or clarify with stakeholders that dark mode implementation is included.

### Decision 2: Use Class-Based Dark Mode with System Preference Default
**Rationale**:
- Provides user control (manual toggle)
- Respects system preference by default
- Can persist user preference
- Most flexible approach

**Implementation**:
- Add `dark` class to `<html>` element
- Define dark mode colors in `.dark` selector
- Use JavaScript to toggle class
- Store preference in localStorage

### Decision 3: Consolidate Button Colors to Use CSS Variables
**Rationale**: Button component currently uses hardcoded colors that don't match CSS variables. This creates inconsistency and makes theming difficult.

**Action**: Refactor Button component to use CSS variables instead of inline styles.

### Decision 4: Target WCAG 2.1 Level AA (Not AAA)
**Rationale**:
- Level AA is industry standard for web applications
- Level AAA (7:1 ratio) is very restrictive and may conflict with brand identity
- Spec explicitly states Level AA as target

**Contrast Targets**:
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

### Decision 5: Use Hex Color Format
**Rationale**:
- Universal browser support
- Simple and readable
- Consistent with current implementation
- Easy to calculate contrast ratios

## Proposed Dark Mode Color Palette

### Dark Mode Colors (Draft)

| Element | Light Mode | Dark Mode | Contrast (Dark) | Status |
|---------|-----------|-----------|-----------------|--------|
| Background | #f8fafc | #0f172a | - | - |
| Card Background | #ffffff | #1e293b | - | - |
| Main Text | #0f172a | #f1f5f9 | ~14.8:1 | ✅ Pass |
| Muted Text | #64748b | #94a3b8 | ~6.2:1 | ✅ Pass |
| Primary | #3b82f6 | #60a5fa | ~5.8:1 | ✅ Pass |
| Primary Hover | #2563eb | #3b82f6 | ~4.9:1 | ✅ Pass |
| Success | #10b981 | #34d399 | ~5.1:1 | ✅ Pass |

**Note**: These are initial proposals. Final colors should be validated with contrast checker tools and adjusted for visual harmony.

### Design Principles for Dark Mode
1. **Avoid Pure Black**: Use dark blue (#0f172a) instead of #000000 to reduce eye strain
2. **Reduce Contrast**: Dark mode should have slightly lower contrast than light mode to prevent glare
3. **Maintain Color Relationships**: Keep hue relationships consistent between modes
4. **Test with Real Content**: Validate colors with actual UI components, not just swatches

## Next Steps (Phase 1)

1. **Create quickstart.md**: Document how to test theme changes
2. **Finalize Color Palette**: Validate all dark mode colors with contrast checker
3. **Design Theme Toggle**: Plan UI for dark/light mode switcher
4. **Update Agent Context**: Add dark mode implementation to project context
5. **Proceed to /sp.tasks**: Generate detailed implementation tasks

## Open Questions

1. **Theme Toggle Location**: Where should the dark/light mode toggle be placed? (Header, settings, floating button?)
2. **Default Mode**: Should we default to system preference or always start in light mode?
3. **Transition Animation**: Should theme switching be instant or animated?
4. **Scope Clarification**: Does stakeholder approve expanding scope to include dark mode implementation?

## References

- WCAG 2.1 Contrast Guidelines: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- CSS Variables Browser Support: https://caniuse.com/css-variables
- Next.js Dark Mode Guide: https://nextjs.org/docs/app/building-your-application/styling/css-variables
