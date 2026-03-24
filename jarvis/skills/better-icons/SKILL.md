---
name: better-icons
description: 'Use when working with icons in any project. Provides CLI for searching 200+ icon libraries (Iconify) and retrieving SVGs. Commands: `better-icons search <query>` to find icons, `better-icons get <id>` to get SVG. Also available as MCP server for AI agents.'
---

# Better Icons

Search and retrieve icons from 200+ libraries via Iconify.

## CLI

    better-icons search <query> [--prefix <prefix>] [--limit <n>] [--json]
    better-icons search <query> -d [dir] [--color <color>] [--size <px>]
    better-icons get <icon-id> [--color <color>] [--size <px>] [--json]
    better-icons setup [-a cursor,claude-code] [-s global|project]

## Examples

    better-icons search arrow --limit 10
    better-icons search home --json | jq '.icons[0]'
    better-icons get lucide:home > icon.svg
    better-icons get mdi:home --color '#333' --json
    better-icons search arrow -d              # saves to ./icons/
    better-icons search check -d ./my-icons
    better-icons search star -d -c '#000' -s 24 --limit 64

## Icon ID Format

    prefix:name  (e.g., lucide:home, mdi:arrow-right, heroicons:check)

## Popular Collections

    lucide, mdi, heroicons, tabler, ph, ri, solar, iconamoon

## MCP Tools (for AI agents)

    search_icons       - Search across all libraries
    get_icon           - Get single icon SVG
    get_icons          - Batch retrieve multiple icons
    list_collections   - Browse available icon sets
    recommend_icons    - Smart recommendations for use cases
    find_similar_icons - Find variations across collections
    sync_icon          - Add icon to project file
    scan_project_icons - List icons in project

## TypeScript Interfaces

    SearchIcons   { query, limit?, prefix?, category? }
    GetIcon       { icon_id, color?, size? }
    GetIcons      { icon_ids[], color?, size? }
    RecommendIcons { use_case, style?, limit? }
    SyncIcon      { icons_file, framework, icon_id, component_name? }

## API

    All icons from https://api.iconify.design
