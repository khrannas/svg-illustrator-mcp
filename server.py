import json
import os
import math
import random
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("svg-illustrator")

CHARACTERS_DIR = os.path.join(os.path.dirname(__file__), "characters")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

STYLE_COLORS = {
    "storybook": {"bg": "#FFF8F0", "stroke": "#333", "fill_opacity": "0.9", "shadow": "rgba(0,0,0,0.1)"},
    "modern": {"bg": "#FFFFFF", "stroke": "#222", "fill_opacity": "1.0", "shadow": "rgba(0,0,0,0.05)"},
    "cartoon": {"bg": "#FFFAF0", "stroke": "#111", "fill_opacity": "0.95", "shadow": "rgba(0,0,0,0.15)"},
    "watercolor": {"bg": "#F5F0EB", "stroke": "#555", "fill_opacity": "0.85", "shadow": "rgba(0,0,0,0.08)"},
    "night": {"bg": "#1A1A2E", "stroke": "#CCF", "fill_opacity": "0.9", "shadow": "rgba(0,0,0,0.3)"},
    "adventure": {"bg": "#FFF5E6", "stroke": "#2A2A2A", "fill_opacity": "0.95", "shadow": "rgba(0,0,0,0.12)"},
}

SCENE_BG = {
    "outdoor": '<rect width="800" height="600" fill="#87CEEB"/>'
              '<rect y="400" width="800" height="200" fill="#7CCD7C"/>'
              '<circle cx="650" cy="80" r="50" fill="#FFD700" opacity="0.8"/>',
    "indoor": '<rect width="800" height="600" fill="#F5DEB3"/>'
              '<rect y="450" width="800" height="150" fill="#8B4513" opacity="0.6"/>'
              '<rect x="50" y="100" width="700" height="350" fill="#FFF8DC" rx="5"/>',
    "castle": '<rect width="800" height="600" fill="#B0C4DE"/>'
              '<rect y="350" width="800" height="250" fill="#696969"/>'
              '<rect x="300" y="100" width="200" height="250" fill="#A9A9A9"/>'
              '<polygon points="300,100 400,30 500,100" fill="#808080"/>',
    "forest": '<rect width="800" height="600" fill="#98FB98"/>'
              '<rect y="420" width="800" height="180" fill="#228B22"/>'
              '<circle cx="200" cy="250" r="80" fill="#2E8B57"/>'
              '<circle cx="600" cy="200" r="90" fill="#2E8B57"/>',
    "ocean": '<rect width="800" height="600" fill="#4682B4"/>'
             '<rect y="400" width="800" height="200" fill="#4169E1"/>'
             '<path d="M0,400 Q100,380 200,400 Q300,420 400,400 Q500,380 600,400 Q700,420 800,400" fill="none" stroke="#FFF" stroke-width="3" opacity="0.5"/>',
    "space": '<rect width="800" height="600" fill="#0B0B1A"/>'
             '<circle cx="150" cy="80" r="3" fill="#FFF"/>'
             '<circle cx="350" cy="120" r="2" fill="#FFF"/>'
             '<circle cx="500" cy="50" r="4" fill="#FFF"/>'
             '<circle cx="700" cy="150" r="2" fill="#FFF"/>'
             '<circle cx="400" cy="200" r="1.5" fill="#FFF"/>',
    "mountain": '<rect width="800" height="600" fill="#E0E0E0"/>'
                '<polygon points="0,600 200,100 400,600" fill="#696969"/>'
                '<polygon points="300,600 500,80 700,600" fill="#808080"/>'
                '<polygon points="500,600 700,150 800,600" fill="#696969"/>'
                '<polygon points="150,600 350,200 550,600" fill="#A9A9A9"/>',
    "night": '<rect width="800" height="600" fill="#0B0B2E"/>'
             '<circle cx="100" cy="80" r="40" fill="#FFE4B5" opacity="0.8"/>'
             '<circle cx="650" cy="100" r="3" fill="#FFF"/>'
             '<circle cx="500" cy="50" r="2" fill="#FFF"/>'
             '<circle cx="700" cy="180" r="2.5" fill="#FFF"/>'
             '<circle cx="300" cy="60" r="1.5" fill="#FFF"/>',
    "magical": '<rect width="800" height="600" fill="#1A0033"/>'
               '<circle cx="400" cy="100" r="60" fill="#9B59B6" opacity="0.6"/>'
               '<circle cx="200" cy="60" r="2" fill="#FFD700"/>'
               '<circle cx="600" cy="80" r="3" fill="#FFD700"/>'
               '<circle cx="350" cy="150" r="1.5" fill="#FFD700"/>'
               '<circle cx="500" cy="120" r="2" fill="#FFD700"/>',
}

FEATURES = {
    "eyes": {
        "round": '<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/><circle cx="{x2}" cy="{y2}" r="{r}" fill="{color}"/>',
        "happy": '<path d="M{x1},{y} Q{xm},{yd} {x2},{y}" fill="none" stroke="{color}" stroke-width="2"/><path d="M{x3},{y} Q{xm2},{yd} {x4},{y}" fill="none" stroke="{color}" stroke-width="2"/>',
        "closed": '<path d="M{x1},{y} Q{xm},{yd} {x2},{y}" fill="none" stroke="{color}" stroke-width="1.5"/><path d="M{x3},{y} Q{xm2},{yd} {x4},{y}" fill="none" stroke="{color}" stroke-width="1.5"/>',
    },
    "mouth": {
        "smile": '<path d="M{cx-10},{cy} Q{cx},{cy+12} {cx+10},{cy}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>',
        "happy": '<path d="M{cx-12},{cy} Q{cx},{cy+15} {cx+12},{cy}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>',
        "surprised": '<ellipse cx="{cx}" cy="{cy}" rx="5" ry="7" fill="{color}" opacity="0.8"/>',
        "open": '<ellipse cx="{cx}" cy="{cy}" rx="6" ry="8" fill="#333"/>',
        "sad": '<path d="M{cx-10},{cy} Q{cx},{cy-8} {cx+10},{cy}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>',
    },
}

def build_character_svg(char: dict, cx: int, cy: int, scale: float = 1.0, expression: str = "happy") -> list[str]:
    parts = []
    colors = char.get("colors", {})
    skin = colors.get("skin", "#FFDAB9")
    hair = colors.get("hair", "#8B4513")
    eye_color = colors.get("eyes", "#333")
    outfit = colors.get("outfit", "#E74C3C")
    
    r = int(30 * scale)
    body_h = int(60 * scale)
    body_w = int(40 * scale)
    
    # Body
    parts.append(f'<ellipse cx="{cx}" cy="{cy + r + body_h//2}" rx="{body_w//2}" ry="{body_h//2}" fill="{outfit}" stroke="#333" stroke-width="1.5"/>')
    
    # Head
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{skin}" stroke="#333" stroke-width="1.5"/>')
    
    # Hair
    hair_y = cy - int(r * 0.7)
    parts.append(f'<path d="M{cx - r},{cy} Q{cx - r},{cy - r} {cx},{cy - r} Q{cx + r},{cy - r} {cx + r},{cy}" fill="{hair}" stroke="#333" stroke-width="1"/>')
    
    # Eyes
    eye_r = int(5 * scale)
    eye_y = cy - int(2 * scale)
    eye_offset = int(12 * scale)
    feat = FEATURES["eyes"].get(char.get("eye_style", "round"))
    if feat:
        parts.append(feat.format(
            x=cx - eye_offset - eye_r//2, x2=cx - eye_offset + eye_r//2, y=eye_y, r=eye_r, color=eye_color,
            x1=cx - eye_offset - 8, xm=cx - eye_offset, x2=cx - eye_offset + 8, yd=eye_y + 3,
            x3=cx + eye_offset - 8, xm2=cx + eye_offset, x4=cx + eye_offset + 8, xm3=cx, yd2=eye_y + 3,
            color=eye_color
        ))
    
    # Mouth
    mouth_y = cy + int(10 * scale)
    mouth_feat = FEATURES["mouth"].get(expression if expression in FEATURES["mouth"] else "happy")
    if mouth_feat:
        parts.append(mouth_feat.format(cx=cx, cy=mouth_y, color="#333"))
    
    return parts

def build_scene_svg(scene: str, characters: list[dict], style: str = "storybook") -> str:
    bg_html = SCENE_BG.get(scene, SCENE_BG["outdoor"])
    style_colors = STYLE_COLORS.get(style, STYLE_COLORS["storybook"])
    
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">',
        f'<defs><filter id="shadow"><feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="{style_colors["shadow"]}"/></filter></defs>',
        bg_html
    ]
    
    # Place characters
    char_positions = [
        (200, 300, 1.0),  # left-center
        (400, 280, 1.1),  # center
        (600, 300, 1.0),  # right-center
    ]
    
    for i, char in enumerate(characters[:3]):
        cx, cy, sc = char_positions[i]
        svg_parts = build_character_svg(char, cx, cy, sc, char.get("expression", "happy"))
        parts.extend(svg_parts)
    
    parts.append('</svg>')
    return "\n".join(parts)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_character_profile",
            description="Create a reusable character definition with SVG components",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"},
                    "colors": {
                        "type": "object",
                        "properties": {
                            "skin": {"type": "string", "description": "Skin color hex"},
                            "hair": {"type": "string", "description": "Hair color hex"},
                            "eyes": {"type": "string", "description": "Eye color hex"},
                            "outfit": {"type": "string", "description": "Outfit color hex"},
                        },
                        "required": ["skin", "hair", "eyes", "outfit"]
                    },
                    "eye_style": {"type": "string", "enum": ["round", "happy", "closed"]},
                    "features": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "colors"]
            }
        ),
        types.Tool(
            name="generate_page_illustration",
            description="Generate a full-page SVG illustration for a story page",
            inputSchema={
                "type": "object",
                "properties": {
                    "characters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "expression": {"type": "string", "enum": ["happy", "sad", "surprised", "scared", "angry", "neutral"]}
                            }
                        }
                    },
                    "background": {"type": "string", "enum": ["outdoor", "indoor", "castle", "forest", "ocean", "space", "mountain", "night", "magical"]},
                    "mood": {"type": "string"},
                    "page_number": {"type": "integer"},
                    "style": {"type": "string", "enum": ["storybook", "modern", "cartoon", "watercolor", "night", "adventure"]},
                },
                "required": ["characters", "background", "page_number"]
            }
        ),
        types.Tool(
            name="generate_story_illustrations",
            description="Batch generate all illustrations for a story",
            inputSchema={
                "type": "object",
                "properties": {
                    "characters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "colors": {
                                    "type": "object",
                                    "properties": {
                                        "skin": {"type": "string"},
                                        "hair": {"type": "string"},
                                        "eyes": {"type": "string"},
                                        "outfit": {"type": "string"}
                                    }
                                },
                                "eye_style": {"type": "string"}
                            }
                        }
                    },
                    "pages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "page_number": {"type": "integer"},
                                "description": {"type": "string"},
                                "background": {"type": "string"},
                                "mood": {"type": "string"},
                                "expressions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    },
                    "output_dir": {"type": "string"},
                    "style": {"type": "string"},
                },
                "required": ["characters", "pages"]
            }
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    if name == "generate_character_profile":
        char_name = arguments["name"]
        char_file = os.path.join(CHARACTERS_DIR, f"{char_name.lower().replace(' ', '-')}.json")
        char_data = {
            "name": char_name,
            "colors": arguments.get("colors", {"skin": "#FFDAB9", "hair": "#8B4513", "eyes": "#333", "outfit": "#E74C3C"}),
            "eye_style": arguments.get("eye_style", "round"),
            "features": arguments.get("features", []),
        }
        with open(char_file, "w") as f:
            json.dump(char_data, f, indent=2)
        return [types.TextContent(type="text", text=f"Character '{char_name}' saved to {char_file}")]
    
    elif name == "generate_page_illustration":
        style = arguments.get("style", "storybook")
        bg = arguments.get("background", "outdoor")
        page_num = arguments.get("page_number", 1)
        
        char_list = arguments.get("characters", [])
        chars = []
        for c in char_list:
            cf = os.path.join(CHARACTERS_DIR, f"{c['name'].lower().replace(' ', '-')}.json")
            if os.path.exists(cf):
                with open(cf) as f:
                    chars.append(json.load(f))
            else:
                chars.append({
                    "name": c["name"],
                    "colors": {"skin": "#FFDAB9", "hair": "#8B4513", "eyes": "#333", "outfit": "#E74C3C"},
                    "expression": c.get("expression", "happy"),
                })
            chars[-1]["expression"] = c.get("expression", "happy")
        
        svg = build_scene_svg(bg, chars, style)
        filename = f"page-{page_num:02d}.svg"
        filepath = os.path.join(OUTPUTS_DIR, filename)
        with open(filepath, "w") as f:
            f.write(svg)
        
        return [types.TextContent(type="text", text=f"Illustration saved to {filepath}\n\n```svg\n{svg[:500]}...\n```")]
    
    elif name == "generate_story_illustrations":
        chars_raw = arguments.get("characters", [])
        pages = arguments.get("pages", [])
        output_dir = arguments.get("output_dir", OUTPUTS_DIR)
        style = arguments.get("style", "storybook")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save character profiles
        for c in chars_raw:
            cf = os.path.join(CHARACTERS_DIR, f"{c['name'].lower().replace(' ', '-')}.json")
            with open(cf, "w") as f:
                json.dump(c, f, indent=2)
        
        # Generate illustrations
        generated = []
        for page in pages:
            pn = page.get("page_number", 1)
            bg = page.get("background", "outdoor")
            chars = []
            for i, c in enumerate(chars_raw):
                expr = "happy"
                if "expressions" in page and i < len(page["expressions"]):
                    expr = page["expressions"][i]
                with open(os.path.join(CHARACTERS_DIR, f"{c['name'].lower().replace(' ', '-')}.json")) as f:
                    ch = json.load(f)
                ch["expression"] = expr
                chars.append(ch)
            
            svg = build_scene_svg(bg, chars, style)
            filename = f"page-{pn:02d}.svg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(svg)
            generated.append(filename)
        
        return [types.TextContent(type="text", text=f"Generated {len(generated)} illustrations: {', '.join(generated)}")]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="svg-illustrator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
