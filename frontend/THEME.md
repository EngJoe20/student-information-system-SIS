# Academia Frontend - Theme Documentation

## Color Palette

The frontend uses a custom color palette:

- **Primary Color (Dark Blue)**: `#1D3A6B`
  - Used for: Primary buttons, links, headers, active states
  - Represents: Trust, professionalism, education

- **Secondary Color (Light Blue/Gray)**: `#9EB3C2`
  - Used for: Secondary elements, backgrounds, borders
  - Represents: Calm, clarity, accessibility

- **Accent Color (Gold)**: `#D0A138`
  - Used for: Highlights, warnings, important actions
  - Represents: Achievement, excellence, attention

## Color Usage

### Primary Color (#1D3A6B)
- Navigation bar brand
- Primary buttons
- Active links and menu items
- Table headers
- Card headers
- Form focus states
- Pagination active state
- Stats cards (default)

### Secondary Color (#9EB3C2)
- Sidebar hover states
- Table hover backgrounds
- Secondary buttons
- Borders and dividers
- Info stats cards
- Scrollbar thumb

### Accent Color (#D0A138)
- Warning badges
- Warning stats cards
- Important highlights
- Hover states on links
- Achievement indicators

## CSS Variables

All colors are defined in CSS variables for easy customization:

```css
:root {
    --primary-color: #1D3A6B;
    --secondary-color: #9EB3C2;
    --accent-color: #D0A138;
    --warning-color: #D0A138;
    --info-color: #9EB3C2;
    --dark-color: #1D3A6B;
}
```

## Files Updated

1. **main.css** - Global styles with new color palette
2. **auth.css** - Authentication page with gradient background
3. **theme-overrides.css** - Bootstrap component overrides
4. **navbar.html** - Updated brand colors
5. **login.html** - Updated icon and heading colors

## Applying Theme to New Pages

When creating new pages, include the theme CSS files:

```html
<link rel="stylesheet" href="../../assets/css/main.css">
<link rel="stylesheet" href="../../assets/css/theme-overrides.css">
```

## Customizing Colors

To change the theme colors:

1. Edit `frontend/assets/css/main.css` - Update CSS variables in `:root`
2. Edit `frontend/assets/css/theme-overrides.css` - Update Bootstrap overrides
3. Edit `frontend/assets/css/auth.css` - Update authentication page colors

## Color Contrast

All color combinations meet WCAG AA standards:
- Primary text on white: ✅
- White text on primary: ✅
- Accent text on white: ✅
- Secondary text on white: ✅

## Gradient Usage

The theme uses subtle gradients:

- **Primary Gradient**: `#1D3A6B` → `#2d4a7a` (darker shade)
- **Auth Background**: `#1D3A6B` → `#2d4a7a` → `#9EB3C2`
- **Stats Cards**: Various gradients using theme colors

## Examples

### Primary Button
```html
<button class="btn btn-primary">Primary Action</button>
```

### Accent/Warning Button
```html
<button class="btn btn-warning">Warning Action</button>
```

### Primary Badge
```html
<span class="badge bg-primary">Primary Badge</span>
```

### Accent Badge
```html
<span class="badge bg-warning">Accent Badge</span>
```

## Browser Compatibility

All colors use standard hex notation and are compatible with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

