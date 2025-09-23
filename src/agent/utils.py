"""
Enhanced utility functions with SVG fallback for graph visualization.
"""

import os
import time
import random
from typing import Optional
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from typing import List, Annotated
from textwrap import dedent
from langchain_core.tools import tool, BaseTool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState


def save_graph_image(graph, filename: str, max_retries: int = 2, retry_delay: float = 2.0) -> Optional[str]:
    """
    Save graph visualization with retry logic and SVG fallback.
    
    Args:
        graph: LangGraph graph object
        filename: Name for the output file (without extension)
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries in seconds
        
    Returns:
        str: Path to the saved image file, or None if all attempts failed
    """
    # Create images directory if it doesn't exist
    os.makedirs("images", exist_ok=True)
    filepath = f"images/{filename}.png"
    
    print(f"🎨 Generating graph image: {filename}")
    
    # Try PNG generation with retries
    for attempt in range(max_retries):
        try:
            # Get PNG bytes from LangGraph
            graph_png = graph.get_graph().draw_mermaid_png()
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(graph_png)
            
            print(f"✅ Graph saved successfully: {filename}")
            return filepath
            
        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️ Attempt {attempt + 1}/{max_retries} failed for {filename}: {e}")
                print(f"🔄 Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print(f"❌ PNG generation failed for {filename}: {e}")
    
    # PNG failed, try SVG fallback
    return _generate_svg_fallback(graph, filename)


def _generate_svg_fallback(graph, filename: str) -> Optional[str]:
    """Generate SVG visualization as fallback when PNG fails."""
    print(f"🔄 Generating SVG fallback for {filename}")
    
    try:
        # Get the graph structure
        graph_obj = graph.get_graph()
        nodes = list(graph_obj.nodes.keys())
        edges = graph_obj.edges
        
        # Debug info
        print(f"  Nodes found: {nodes}")
        print(f"  Number of edges: {len(edges) if hasattr(edges, '__len__') else 'unknown'}")
        
        # Create a simple SVG based on the graph structure
        svg_content = _create_svg_from_graph_structure(nodes, edges, filename)
        
        svg_filepath = f"images/{filename}.svg"
        with open(svg_filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"✅ SVG fallback saved: {filename}.svg")
        return svg_filepath
        
    except Exception as e:
        print(f"❌ SVG fallback failed for {filename}: {e}")
        import traceback
        traceback.print_exc()
        
        # Last resort: save Mermaid source
        try:
            mermaid_source = graph.get_graph().draw_mermaid()
            mermaid_filepath = f"images/{filename}.mmd"
            
            with open(mermaid_filepath, "w", encoding="utf-8") as f:
                f.write(mermaid_source)
            
            print(f"📝 Mermaid source saved: {filename}.mmd")
            print("💡 You can render this manually at: https://mermaid.live/")
            return mermaid_filepath
            
        except Exception as e2:
            print(f"❌ All fallbacks failed for {filename}: {e2}")
            return None


def _create_svg_from_graph_structure(nodes: list, edges: list, filename: str) -> str:
    """Create a basic SVG representation of the graph structure."""
    
    # Define SVG dimensions and styling
    width = 800
    height = 600
    node_width = 120
    node_height = 60
    
    # Calculate positions for nodes
    num_nodes = len(nodes)
    positions = {}
    
    try:
        if "supervisor" in [n.lower() for n in nodes]:
            # Special layout for supervisor graphs
            supervisor_node = next((n for n in nodes if "supervisor" in n.lower()), nodes[0])
            positions[supervisor_node] = (width // 2, 200)
            
            other_nodes = [n for n in nodes if n != supervisor_node and n not in ["__start__", "__end__"]]
            
            # Arrange other nodes in a row below supervisor
            if other_nodes:
                spacing = min(200, (width - 100) // max(1, len(other_nodes)))
                start_x = (width - (len(other_nodes) - 1) * spacing) // 2
                
                for i, node in enumerate(other_nodes):
                    positions[node] = (start_x + i * spacing, 400)
            
            # Add start and end positions
            if "__start__" in nodes:
                positions["__start__"] = (width // 2, 80)
            if "__end__" in nodes:
                positions["__end__"] = (width // 2, 520)
        
        else:
            # Default circular layout
            import math
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 3
            
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / max(1, num_nodes)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[node] = (x, y)
                
    except Exception as e:
        print(f"  Error calculating positions, using fallback: {e}")
        # Fallback: simple grid layout
        cols = max(1, int(num_nodes**0.5))
        rows = max(1, (num_nodes + cols - 1) // cols)
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = 100 + col * (width - 200) // max(1, cols - 1) if cols > 1 else width // 2
            y = 100 + row * (height - 200) // max(1, rows - 1) if rows > 1 else height // 2
            positions[node] = (x, y)
    
    # Generate SVG content
    svg_lines = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect width="{width}" height="{height}" fill="#f8f9fa"/>',
        f'  <text x="{width//2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#2c3e50">{filename.replace("_", " ").title()}</text>',
        '  <defs>',
        '    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
        '      <polygon points="0 0, 10 3.5, 0 7" fill="#2c3e50"/>',
        '    </marker>',
        '  </defs>',
    ]
    
    # Add edges
    for edge in edges:
        try:
            # Handle different edge types more robustly
            start_node = None
            end_node = None
            
            if hasattr(edge, 'start_key') and hasattr(edge, 'end_key'):
                start_node = edge.start_key
                end_node = edge.end_key
            elif hasattr(edge, 'source') and hasattr(edge, 'target'):
                start_node = edge.source
                end_node = edge.target
            elif isinstance(edge, tuple) and len(edge) >= 2:
                start_node = edge[0]
                end_node = edge[1]
            elif isinstance(edge, str) and ' -> ' in edge:
                parts = edge.split(' -> ')
                if len(parts) >= 2:
                    start_node = parts[0].strip()
                    end_node = parts[1].strip()
            else:
                # Try to extract from string representation
                edge_str = str(edge)
                if ' -> ' in edge_str:
                    parts = edge_str.split(' -> ')
                    if len(parts) >= 2:
                        start_node = parts[0].strip()
                        end_node = parts[1].strip()
                elif '->' in edge_str:
                    parts = edge_str.split('->')
                    if len(parts) >= 2:
                        start_node = parts[0].strip()
                        end_node = parts[1].strip()
            
            # Only draw edge if we successfully parsed both nodes
            if start_node and end_node and start_node in positions and end_node in positions:
                x1, y1 = positions[start_node]
                x2, y2 = positions[end_node]
                
                # Adjust line endpoints to node boundaries
                dx, dy = x2 - x1, y2 - y1
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    # Start from edge of start node
                    x1 += (node_width // 2) * (dx / length)
                    y1 += (node_height // 2) * (dy / length)
                    # End at edge of end node
                    x2 -= (node_width // 2) * (dx / length)
                    y2 -= (node_height // 2) * (dy / length)
                
                svg_lines.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2c3e50" stroke-width="2" marker-end="url(#arrowhead)"/>')
            else:
                print(f"  Skipping edge: {edge} (could not parse or nodes not found)")
                
        except Exception as e:
            print(f"  Error processing edge {edge}: {e}")
            continue
    
    # Add nodes
    colors = {
        "supervisor": "#007bff",
        "research": "#17a2b8", 
        "portfolio": "#6f42c1",
        "trading": "#fd7e14",
        "__start__": "#28a745",
        "__end__": "#dc3545"
    }
    
    for node in nodes:
        if node in positions:
            x, y = positions[node]
            
            # Choose color based on node name
            color = "#6c757d"  # default
            for keyword, node_color in colors.items():
                if keyword in node.lower():
                    color = node_color
                    break
            
            # Special handling for start/end nodes (circles)
            if node in ["__start__", "__end__"]:
                svg_lines.extend([
                    f'  <circle cx="{x}" cy="{y}" r="25" fill="{color}" stroke="#2c3e50" stroke-width="2"/>',
                    f'  <text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="white">{node.replace("__", "").upper()}</text>'
                ])
            else:
                # Regular nodes (rectangles)
                svg_lines.extend([
                    f'  <rect x="{x - node_width//2}" y="{y - node_height//2}" width="{node_width}" height="{node_height}" rx="8" fill="{color}" stroke="#2c3e50" stroke-width="2"/>',
                    f'  <text x="{x}" y="{y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="white">{node.replace("_", " ").title()}</text>'
                ])
    
    svg_lines.append('</svg>')
    
    return '\n'.join(svg_lines)


# Keep the original utility functions
def print_messages(messages, truncate_length=200):
    """Print messages with truncation for long tool message content."""
    for message in messages:
        if isinstance(message, ToolMessage):
            print(f"=================================[1m Tool Message [0m=================================")
            print(f"Name: {message.name}\n")
            
            content = message.content
            if len(content) > truncate_length:
                print(f"{content[:truncate_length]}...\n[Content truncated - {len(content)} chars total]")
            else:
                print(content)
        else:
            message.pretty_print()


def _normalize_agent_name(agent_name: str) -> str:
    """Convert an agent name to a valid tool name format (snake_case)."""
    return agent_name.replace(" ", "_").lower()


def create_handoff_tool(*, agent_name: str, name: str | None = None, description: str | None = None) -> BaseTool:
    """Create a tool that transfers control to another agent with specific task instructions."""
    if name is None:
        name = f"transfer_to_{_normalize_agent_name(agent_name)}"
    if description is None:
        description = f"Ask agent '{agent_name}' for help"

    @tool(name, description=description)
    def handoff_to_agent(
        instructions: str,
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """
        Transfer control to another agent with specific instructions.
        
        Args:
            instructions: Specific task instructions for the target agent
        """
        tool_message = ToolMessage(
            content=dedent(f"""
            Successfully transferred to {agent_name}.
            Task instructions: {instructions}
            """),
            name=name,
            tool_call_id=tool_call_id
        )

        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "messages": state["messages"] + [tool_message]
            },
        )
    return handoff_to_agent


def get_graph_image_bytes(graph, filename_hint: str = "graph"):
    """
    Get graph visualization as bytes for Streamlit display.
    
    Args:
        graph: LangGraph graph object
        filename_hint: Hint about the graph type
        
    Returns:
        bytes: PNG image data or None if failed
    """
    print(f"🎨 Getting graph bytes for Streamlit")
    
    try:
        graph_png = graph.get_graph().draw_mermaid_png()
        print(f"✅ Graph bytes generated successfully")
        return graph_png
        
    except Exception as e:
        print(f"⚠️ Failed to get graph bytes: {e}")
        return None


def ensure_images_exist(graph_dict: dict, force_recreate: bool = False):
    """
    Ensure all graph images exist in the images folder.
    
    Args:
        graph_dict: Dictionary of {filename: graph} pairs
        force_recreate: If True, recreate all images even if they exist
    """
    print("🖼️ Ensuring graph images exist...")
    
    for filename, graph in graph_dict.items():
        filepath = f"images/{filename}.png"
        svg_filepath = f"images/{filename}.svg"
        
        if force_recreate or not (os.path.exists(filepath) or os.path.exists(svg_filepath)):
            print(f"Creating image: {filename}")
            save_graph_image(graph, filename)
        else:
            print(f"✅ Image already exists: {filename}")

    print("🎨 All images ready!")