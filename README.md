# SVG Illustrator MCP Server

MCP server that generates SVG illustrations for children's story pages. Character-consistent, theme-aware, zero cost.

## Tools

### generate_character_profile
Creates a reusable character definition as SVG components.

Parameters:
- name: character name
- colors: skin, hair, eyes, outfit colors
- features: eye style, mouth style, accessories
- proportions: width, height relative to standard

### generate_page_illustration
Generates a full-page SVG illustration.

Parameters:
- characters: list of character names and positions
- background: scene type (outdoor, indoor, castle, forest, ocean, space, mountain, night, magical)
- mood: happy, sad, adventurous, calm, scary
- page_number: for file naming

### generate_story_illustrations
Batch generates all illustrations for a story.

Parameters:
- characters: list of character definitions
- pages: list of page descriptions
- output_dir: where to save SVGs
- style: storybook, modern, cartoon, watercolor, night, adventure

## Setup

```bash
pip install -r requirements.txt
python server.py
```

## Configuration

Add to config.yaml:

```yaml
native_mcp:
  servers:
    - name: svg-illustrator
      transport: stdio
      command: python3 /path/to/server.py
```
