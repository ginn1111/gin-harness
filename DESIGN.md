---
version: alpha
name: VS Code Operator Suite
description: A VS Code Dark-inspired visual system for Starship, Kitty, Neovim, Lualine, Herdr, and Hermes profiles Gintary and Ginb.
colors:
  canvas: "#1E1E1E"
  surface: "#252526"
  surface-raised: "#2D2D30"
  surface-active: "#3A3D41"
  border: "#414140"
  text: "#CCCCCC"
  text-bright: "#FFFFFF"
  text-muted: "#858585"
  selection: "#264F78"
  primary: "#569CD6"
  cyan: "#4EC9B0"
  green: "#6A9955"
  green-terminal: "#23D18B"
  yellow: "#DCDCAA"
  orange: "#CE9178"
  red: "#F14C4C"
  purple: "#C586C0"
typography:
  terminal:
    fontFamily: Hack Nerd Font
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1.2
  interface:
    fontFamily: system-ui
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: system-ui
    fontSize: 0.875rem
    fontWeight: 600
    lineHeight: 1.2
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
rounded:
  none: 0px
  sm: 3px
  md: 6px
components:
  terminal:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.text}"
    typography: "{typography.terminal}"
    padding: "{spacing.xs}"
  selection:
    backgroundColor: "{colors.selection}"
    textColor: "{colors.text-bright}"
  statusline:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.text}"
    typography: "{typography.label}"
  statusline-inactive:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.text-muted}"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
  panel-active:
    backgroundColor: "{colors.surface-active}"
    textColor: "{colors.text-bright}"
  profile-gintary:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.primary}"
  profile-ginb:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.green-terminal}"
---

## Overview

One dark operator environment across shell, terminal, editor, statusline, multiplexer, and agent profiles. Base appearance follows VS Code Dark: neutral charcoal surfaces, restrained borders, readable gray text, blue selection, and semantic syntax colors.

Consistency matters more than exact feature parity. Each tool maps native capabilities onto shared tokens. Gintary and Ginb remain visibly distinct without becoming separate themes: Gintary uses blue for coordination and review; Ginb uses green for implementation and successful execution.

## Colors

- **Canvas (`#1E1E1E`):** Primary background for Kitty, Neovim, Herdr, and Hermes TUI.
- **Surface (`#252526`):** Panels, completion menus, sidebars, and inactive tabs.
- **Raised surface (`#2D2D30`):** Popovers and focused secondary regions.
- **Selection (`#264F78`):** Selected text, active completion rows, and visual selections.
- **Text (`#CCCCCC`):** Default foreground. Bright white is reserved for active emphasis.
- **Blue (`#569CD6`):** Gintary identity, keywords, active navigation, and informational state.
- **Green (`#6A9955`):** Strings, additions, and success. Terminal green may use `#23D18B` for stronger contrast.
- **Yellow (`#DCDCAA`):** Functions and warnings.
- **Orange (`#CE9178`):** Literals, modified state, and secondary warnings.
- **Red (`#F14C4C`):** Errors and destructive state.
- **Purple (`#C586C0`):** Control flow and special syntax.

Do not restore Matrix neon colors inside this theme. Do not use accent colors as large backgrounds.

## Typography

Kitty and terminal-facing surfaces use Hack Nerd Font at 11px. Nerd Font glyphs provide prompt, Git, language, and status icons. Neovim inherits terminal typography.

Herdr and Hermes use native interface fonts where terminal font control is unavailable. Labels use semibold weight; body text stays regular. Avoid italics except code comments and language syntax where tool defaults require them.

## Layout

Keep density close to VS Code. Use 4px for terminal padding, 8px between compact status elements, and 16px for panel content. Borders stay one pixel where supported. Corners remain square or lightly rounded; terminal and editor regions should not look card-heavy.

Starship keeps a compact left prompt for identity, host, directory, Git branch, Git status, and prompt character. Language runtimes, duration, and time remain right-aligned. Lualine follows same information hierarchy inside Neovim.

## Elevation & Depth

Use color shifts, not shadows. Canvas, surface, raised surface, and active surface create depth. Popovers may use `surface-raised`; active rows use `selection` or `surface-active`. Terminal-native tools must avoid fake drop shadows.

## Shapes

Use `rounded.none` for terminal panes, statuslines, and editor chrome. Use `rounded.sm` for completion rows or native UI controls. Reserve `rounded.md` for standalone dialogs. Icons should use existing Nerd Font symbols and remain single-color.

## Components

- **Starship:** Rename Matrix palette to VS Code. Use blue for directory and profile identity, cyan for host/runtime metadata, green for clean/success, yellow for Git branch and warnings, red for errors.
- **Kitty:** Use canvas background, default gray foreground, blue selection, white cursor, and VS Code terminal ANSI colors.
- **Neovim:** Use `Mofiqul/vscode.nvim`, dark style, opaque canvas, and native VS Code syntax mapping.
- **Lualine:** Use canvas background. Default text gray. Mode and diagnostic accents use shared semantic colors. Avoid solid high-saturation section blocks.
- **Herdr:** Use Vesper as closest built-in base, then override custom tokens with this palette. Panels use surface levels; focus and links use blue.
- **Gintary profile:** Blue primary and prompt. Cyan tool activity. Purple thinking state. Role reads as coordinator, reviewer, and decision owner.
- **Ginb profile:** Green primary and prompt. Cyan tool activity. Yellow thinking state. Role reads as builder, verifier, and delivery owner.

## Do's and Don'ts

- Do preserve shared canvas, text, selection, and semantic status colors across every tool.
- Do retain profile distinction through primary accent only.
- Do test text/background pairs for WCAG AA where tool rendering permits.
- Do keep prompt and statusline compact.
- Don't use Matrix green as global foreground.
- Don't create a separate palette for each app.
- Don't color every segment; neutral text is default.
- Don't encode status by color alone when an icon or label is available.
