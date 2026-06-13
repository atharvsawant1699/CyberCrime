---
name: CyberGuard Pulse
colors:
  surface: '#faf8ff'
  surface-dim: '#d9d9e5'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3fe'
  surface-container: '#ededf9'
  surface-container-high: '#e7e7f3'
  surface-container-highest: '#e1e2ed'
  on-surface: '#191b23'
  on-surface-variant: '#434655'
  inverse-surface: '#2e3039'
  inverse-on-surface: '#f0f0fb'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#784b00'
  on-tertiary: '#ffffff'
  tertiary-container: '#996100'
  on-tertiary-container: '#ffeedd'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#faf8ff'
  on-background: '#191b23'
  surface-variant: '#e1e2ed'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-base:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-caps:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style

The design system is engineered to bridge the gap between accessible civic duty and high-stakes digital defense. It operates on a dual-modality principle: the **Citizen Surface** and the **Intelligence Core**. 

The **Citizen Surface** employs a **Minimalist Modern** style. It prioritizes clarity, whitespace, and high legibility to reduce cognitive load for users reporting sensitive incidents. The aesthetic is "Trusted Authority"—stable, clean, and professional.

The **Intelligence Core** (SOC Dashboard) shifts into **Technical Glassmorphism**. This environment is high-tech and immersive, utilizing deep-space backgrounds and translucent layers to simulate a sophisticated command-and-control interface. It evokes "Predictive Security"—vibrant, precise, and cutting-edge.

The overall brand personality is one of unwavering protection and clinical precision.

## Colors

This design system utilizes a high-contrast palette optimized for both immediate recognition and long-duration monitoring.

- **Cyber Blue (#2563eb)**: The primary anchor. It represents trust and systemic logic. Used for primary actions, active states, and brand signatures.
- **Success Green (#10b981)**: Denotes "Clean/Secure" status. High saturation for visibility against both light and dark backgrounds.
- **Warning Orange (#f59e0b)**: Used for medium-risk indicators and pending reports.
- **Danger Red (#ef4444)**: Reserved for critical breaches and urgent cybercrime alerts.

The **Light Mode** uses a series of cool-toned grays to maintain a professional atmosphere, while the **Dark Mode** (SOC Dashboard) is anchored by a deep obsidian background (#0a0e17) to allow vibrant data visualizations to pop.

## Typography

The design system exclusively uses **Outfit** for its geometric clarity and technical rhythm. The typeface's open counters and modern proportions lend themselves perfectly to both long-form reporting and rapid-glance dashboarding.

For technical data strings, IP addresses, and hash values within the SOC dashboard, a secondary monospaced font (**JetBrains Mono**) is introduced to ensure character distinction (e.g., distinguishing between '0' and 'O').

Hierarchy is established through weight and tracking rather than just size. Display styles use tighter tracking to feel "industrial," while body text uses generous line heights for accessibility.

## Layout & Spacing

The design system follows a **12-column fluid grid** for the Citizen Surface and a **modular flexible grid** for the SOC Dashboard.

1. **Citizen Surface**: Content is centered within a 1280px container. Large vertical gaps (64px+) separate sections to create a calm, premium reading experience.
2. **SOC Dashboard**: Content is edge-to-edge (fluid) to maximize screen real estate for data widgets. It uses a 24px gutter to maintain clear separation between high-density cards.

The spacing rhythm is strictly 8px-based. Every margin, padding, and height must be a multiple of 8px to ensure a rigid, engineering-led appearance.

## Elevation & Depth

Depth is treated differently across the two modes to define the user's focus:

**Citizen Surface (Light):**
Uses **Tonal Layers**. Elements sit on a subtle #F8FAFC background. Primary cards use a white fill with a soft, expansive shadow (0px 10px 15px -3px rgba(0, 0, 0, 0.05)) to suggest stability and safety.

**Intelligence Core (Dark):**
Uses **Glassmorphism**. Surfaces are semi-transparent (background-blur: 12px) with a 1px border. The border is a subtle linear gradient (Top-Left: White 10%, Bottom-Right: White 0%) to simulate light catching the edge of glass. A "subtle glow" is applied to critical status cards using a colored outer-glow filter matching the status color (e.g., Red for active threats).

## Shapes

The design system uses a **Rounded** shape language to soften the "harsh" nature of cybercrime content and make the technology feel more approachable.

- **Standard Elements**: 0.5rem (8px) for buttons, inputs, and standard cards.
- **Dashboard Modules**: 1rem (16px) for glassmorphic widgets to emphasize the "contained" nature of the data.
- **Status Pills**: Fully rounded (pill-shaped) for instant identification of badges and tags.

## Components

### Buttons
- **Primary**: Solid Cyber Blue with white text. High-contrast, 8px radius.
- **Ghost (SOC)**: Transparent background, 1px Cyber Blue border, subtle hover glow.
- **Danger**: Solid Red, used exclusively for "Delete Data" or "Stop Process" in the SOC.

### Cards
- **Citizen Card**: Flat white, 1px border (#E2E8F0), soft shadow. Focuses on content hierarchy.
- **Glass Widget**: Background #0a0e17 at 60% opacity, 16px blur. Title bar is slightly darker for structural separation.

### Data Tables
- **Standard**: Clean, border-only rows in Light Mode. 
- **SOC High-Density**: Zebra-striping with #FFFFFF05, monospaced fonts for numerical data, and compact vertical padding (8px).

### Timelines
Interactive vertical lines using the primary blue. Incident nodes change color based on severity. In Dark Mode, the line should have a subtle "neon" pulse animation for active tracking.

### Form Fields
- **Inputs**: 1px border with 4px focus ring in Cyber Blue. In Dark Mode, fields are slightly recessed with a darker background than the card surface.