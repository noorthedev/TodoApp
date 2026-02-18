# Quickstart Guide: Frontend Theme Contrast Fix

**Feature**: 001-theme-contrast-fix
**Last Updated**: 2026-02-16

## Overview

This guide provides instructions for testing and validating the theme contrast fix implementation. Use this guide to verify that all text elements meet WCAG 2.1 Level AA accessibility standards in both light and dark modes.

## Prerequisites

- Node.js 18+ installed
- Frontend dependencies installed (`npm install`)
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Internet connection (for accessibility testing tools)

## Running the Application

### Start Development Server

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
cd frontend
npm run build
npm start
```

## Testing Theme Switching

### Manual Theme Toggle

**Current Implementation**: No dark mode toggle exists yet.

**After Implementation**:
1. Locate the theme toggle button (location TBD - likely in header or settings)
2. Click to switch between light and dark modes
3. Verify theme changes instantly (<50ms)
4. Verify preference persists after page reload

### System Preference Testing

**Test System Dark Mode**:
- **macOS**: System Preferences > General > Appearance > Dark
- **Windows**: Settings > Personalization > Colors > Choose your mode > Dark
- **Linux**: Varies by desktop environment

**Expected Behavior**: Application should respect system preference by default (if hybrid approach implemented).

## Contrast Ratio Testing

### Automated Testing with Lighthouse

1. Open Chrome DevTools (F12 or Cmd+Option+I)
2. Navigate to "Lighthouse" tab
3. Select "Accessibility" category
4. Click "Analyze page load"
5. Review "Contrast" section in report

**Expected Result**: Zero contrast-related issues, 100 accessibility score for contrast.

### Automated Testing with axe DevTools

1. Install axe DevTools browser extension:
   - Chrome: https://chrome.google.com/webstore (search "axe DevTools")
   - Firefox: https://addons.mozilla.org/firefox/ (search "axe DevTools")

2. Open extension in DevTools
3. Click "Scan ALL of my page"
4. Review "Contrast" issues

**Expected Result**: Zero contrast violations.

### Manual Contrast Checking

Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/

**Light Mode Verification**:

| Element | Foreground | Background | Expected Ratio | Min Required |
|---------|------------|------------|----------------|--------------|
| Main Text | #0f172a | #f8fafc | ~16.5:1 | 4.5:1 |
| Muted Text | #64748b | #f8fafc | ~5.8:1 | 4.5:1 |
| Primary Button | white | #3b82f6 | ~4.6:1 | 4.5:1 |
| Links | #3b82f6 | #f8fafc | ~5.2:1 | 4.5:1 |

**Dark Mode Verification**:

| Element | Foreground | Background | Expected Ratio | Min Required |
|---------|------------|------------|----------------|--------------|
| Main Text | #f1f5f9 | #0f172a | ~14.8:1 | 4.5:1 |
| Muted Text | #94a3b8 | #0f172a | ~6.2:1 | 4.5:1 |
| Primary Button | white | #60a5fa | ~5.8:1 | 4.5:1 |
| Links | #60a5fa | #0f172a | ~5.8:1 | 4.5:1 |

**How to Check**:
1. Go to https://webaim.org/resources/contrastchecker/
2. Enter foreground color in "Foreground Color" field
3. Enter background color in "Background Color" field
4. Verify "WCAG AA" shows "Pass" for normal text

## Visual Testing Checklist

### Light Mode Testing

Navigate to each page and verify:

- [ ] **Home Page** (`/`)
  - [ ] Title text is clearly readable
  - [ ] Subtitle text is clearly readable
  - [ ] Primary button text is clearly readable
  - [ ] Outline button text is clearly readable
  - [ ] Feature list text is clearly readable
  - [ ] Checkmarks are visible

- [ ] **Login Page** (`/login`)
  - [ ] Form labels are clearly readable
  - [ ] Input text is clearly readable
  - [ ] Button text is clearly readable
  - [ ] Link text is clearly readable
  - [ ] Error messages are clearly readable (if any)

- [ ] **Register Page** (`/register`)
  - [ ] Form labels are clearly readable
  - [ ] Input text is clearly readable
  - [ ] Button text is clearly readable
  - [ ] Link text is clearly readable
  - [ ] Error messages are clearly readable (if any)

- [ ] **Dashboard Page** (`/dashboard`)
  - [ ] Page title is clearly readable
  - [ ] Task list items are clearly readable
  - [ ] Button text is clearly readable
  - [ ] Empty state text is clearly readable (if no tasks)

### Dark Mode Testing

Repeat the same checklist above in dark mode:

- [ ] All pages tested in dark mode
- [ ] No text is too bright (causing glare)
- [ ] No text is too dim (hard to read)
- [ ] Interactive elements are distinguishable

### Interactive Element Testing

Test hover and focus states:

- [ ] **Buttons**
  - [ ] Hover state has sufficient contrast
  - [ ] Focus state is visible
  - [ ] Disabled state is distinguishable

- [ ] **Links**
  - [ ] Default state has sufficient contrast
  - [ ] Hover state is visible
  - [ ] Visited state is distinguishable (if applicable)

- [ ] **Form Inputs**
  - [ ] Placeholder text is readable
  - [ ] Input text is readable
  - [ ] Focus state is visible
  - [ ] Error state is visible

## Zoom Level Testing

Test at different zoom levels to ensure contrast is maintained:

1. **100% Zoom** (default)
   - [ ] All text readable in light mode
   - [ ] All text readable in dark mode

2. **150% Zoom**
   - [ ] All text readable in light mode
   - [ ] All text readable in dark mode
   - [ ] No layout breaking

3. **200% Zoom**
   - [ ] All text readable in light mode
   - [ ] All text readable in dark mode
   - [ ] No layout breaking

**How to Zoom**:
- **Chrome/Firefox/Edge**: Ctrl/Cmd + Plus/Minus
- **Safari**: Cmd + Plus/Minus

## Cross-Browser Testing

Test the application in multiple browsers:

### Chrome
- [ ] Light mode contrast correct
- [ ] Dark mode contrast correct
- [ ] Theme switching works
- [ ] No visual regressions

### Firefox
- [ ] Light mode contrast correct
- [ ] Dark mode contrast correct
- [ ] Theme switching works
- [ ] No visual regressions

### Safari (macOS)
- [ ] Light mode contrast correct
- [ ] Dark mode contrast correct
- [ ] Theme switching works
- [ ] No visual regressions

### Edge (Windows)
- [ ] Light mode contrast correct
- [ ] Dark mode contrast correct
- [ ] Theme switching works
- [ ] No visual regressions

### Mobile Browsers
- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)

## Performance Testing

Verify theme switching performance:

1. Open Chrome DevTools > Performance tab
2. Start recording
3. Toggle theme (light to dark or vice versa)
4. Stop recording
5. Verify theme change completes in <50ms

**Expected Result**: Theme switching should be instant with no visible delay.

## Regression Testing

After implementing theme changes, verify no existing functionality is broken:

- [ ] User can log in
- [ ] User can register
- [ ] User can create tasks
- [ ] User can view tasks
- [ ] User can update tasks
- [ ] User can delete tasks
- [ ] User can log out

## Common Issues & Troubleshooting

### Issue: Contrast ratio fails in Lighthouse but looks fine visually

**Cause**: Lighthouse may detect colors from overlays, shadows, or gradients.

**Solution**:
- Check the specific element flagged
- Verify colors using WebAIM checker
- Adjust colors if needed

### Issue: Dark mode not applying

**Cause**: CSS variables not updating or class not applied.

**Solution**:
- Check if `dark` class is on `<html>` element
- Verify CSS variables are defined in `.dark` selector
- Check browser console for errors

### Issue: Colors look different across browsers

**Cause**: Color rendering differences or CSS variable support issues.

**Solution**:
- Use hex colors instead of RGB/HSL
- Test in all target browsers
- Check for browser-specific CSS bugs

### Issue: Theme preference not persisting

**Cause**: localStorage not working or not implemented.

**Solution**:
- Check browser console for localStorage errors
- Verify theme preference is saved on toggle
- Check if localStorage is cleared on logout

## Validation Criteria

Before marking this feature as complete, ensure:

- ✅ All text elements meet WCAG 2.1 Level AA (4.5:1 for normal text)
- ✅ Lighthouse accessibility score 100 for contrast
- ✅ axe DevTools reports zero contrast violations
- ✅ Manual visual inspection passes in both modes
- ✅ Cross-browser testing passes
- ✅ Zoom level testing passes (100%, 150%, 200%)
- ✅ Theme switching works instantly (<50ms)
- ✅ No regressions in existing functionality

## Next Steps

After validation:

1. Document any issues found
2. Create bug reports for failures
3. Re-test after fixes
4. Get stakeholder approval
5. Prepare for deployment

## Resources

- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Lighthouse Documentation**: https://developers.google.com/web/tools/lighthouse
- **axe DevTools**: https://www.deque.com/axe/devtools/
- **Contrast Ratio Calculator**: https://contrast-ratio.com/
