import os
import json
import re
import gradio as gr
import asyncio

from agents import Agent, Runner, function_tool
from servers.submarine_server import SubmarineCablesServer
from servers.basestation_server import BaseStationCoverageServer
from models import (
    LandingStationResponse, CableRoute, CableLatencyResponse,
    CableOutageRiskResponse, BaseStationResponse, CoverageStrengthResponse,
    ProposedStation, HandoverPathResponse
)

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found. Please set it as an environment variable or in a .env file.\n"
        "You can create a .env file with: OPENAI_API_KEY=your_key_here"
    )

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def build_agent():
    sub = SubmarineCablesServer()
    base = BaseStationCoverageServer()

    @function_tool
    def locate_landing_station(country: str) -> LandingStationResponse:
        return sub._locate_landing_station_impl(country)

    @function_tool
    def cable_route_between(country_a: str, country_b: str) -> CableRoute:
        return sub._cable_route_between_impl(country_a, country_b)

    @function_tool
    def list_cables_near(lat: float, lon: float, radius_km: float) -> list:
        return sub._list_cables_near_impl(lat, lon, radius_km)

    @function_tool
    def cable_latency_estimate(country_a: str, country_b: str) -> CableLatencyResponse:
        return sub._cable_latency_estimate_impl(country_a, country_b)

    @function_tool
    def cable_outage_risk(lat: float, lon: float) -> CableOutageRiskResponse:
        return sub._cable_outage_risk_impl(lat, lon)

    @function_tool
    def nearest_basestations(lat: float, lon: float, radius_km: float) -> BaseStationResponse:
        return base._nearest_basestations_impl(lat, lon, radius_km)

    @function_tool
    def coverage_strength_at(lat: float, lon: float) -> CoverageStrengthResponse:
        return base._coverage_strength_at_impl(lat, lon)

    @function_tool
    def propose_new_station(lat: float, lon: float, required_radius: float) -> ProposedStation:
        return base._propose_new_station_impl(lat, lon, required_radius)

    @function_tool
    def stations_with_capacity(min_capacity: int) -> BaseStationResponse:
        return base._stations_with_capacity_impl(min_capacity)

    @function_tool
    def handover_path(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> HandoverPathResponse:
        return base._handover_path_impl(start_lat, start_lon, end_lat, end_lon)

    tools = [
        locate_landing_station,
        cable_route_between,
        list_cables_near,
        cable_latency_estimate,
        cable_outage_risk,
        nearest_basestations,
        coverage_strength_at,
        propose_new_station,
        stations_with_capacity,
        handover_path
    ]

    agent = Agent(
        name="MapAssistant",
        instructions="You are a helpful map assistant.",
        tools=tools
    )

    return agent


agent = build_agent()


async def ask_agent_async(message: str):
    result = await Runner.run(agent, input=message)
    
    # Try to extract tool results from new_items
    tool_results = []
    if hasattr(result, 'new_items') and result.new_items:
        for item in result.new_items:
            # Check if item has content that might be a tool result
            if hasattr(item, 'content'):
                try:
                    content = item.content
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except:
                            pass
                    if isinstance(content, dict):
                        tool_results.append(content)
                except:
                    pass
    
    return result.final_output, tool_results


def ask_agent(message: str):
    output, tool_results = asyncio.run(ask_agent_async(message))
    return str(output), tool_results


def build_leaflet_map(agent_output, tool_results=None):
    """Build an interactive Leaflet map with markers, lines, and circles."""
    # Always show a map, even if empty
    html = """
    <div id="map" style="height: 100%; width: 100%; min-height: 600px; border-radius: 8px; border: 2px solid #ddd;"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        function animateLine(coords, color='red') {
            var index = 0;
            var polyline = L.polyline([], {color: color, weight: 4, opacity: 0.8}).addTo(map);
            function drawSegment() {
                if (index < coords.length) {
                    polyline.addLatLng(coords[index]);
                    index++;
                    setTimeout(drawSegment, 100);
                }
            }
            drawSegment();
        }
    """
    
    points = []
    lines = []
    circles = []
    
    # Extract from tool results
    if tool_results:
        for result in tool_results:
            if isinstance(result, dict):
                # Base stations
                if "stations" in result:
                    for station in result.get("stations", []):
                        if isinstance(station, dict) and "lat" in station and "lon" in station:
                            points.append({
                                "lat": float(station["lat"]),
                                "lon": float(station["lon"]),
                                "label": f"📡 {station.get('id', 'Base Station')}"
                            })
                
                # Landing stations
                if "landing_stations" in result:
                    for station in result.get("landing_stations", []):
                        if isinstance(station, dict) and "lat" in station and "lon" in station:
                            points.append({
                                "lat": float(station["lat"]),
                                "lon": float(station["lon"]),
                                "label": f"🌐 {station.get('name', 'Landing Station')}"
                            })
                
                # Cable routes
                if "path_coordinates" in result:
                    coords = []
                    for coord in result["path_coordinates"]:
                        if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                            coords.append([float(coord[0]), float(coord[1])])
                    if coords:
                        lines.append({"coords": coords, "color": "#e74c3c"})
                
                # Coverage areas
                if "center" in result and "radius_km" in result:
                    center = result["center"]
                    if isinstance(center, (list, tuple)) and len(center) >= 2:
                        circles.append({
                            "lat": float(center[0]),
                            "lon": float(center[1]),
                            "radius": float(result["radius_km"])
                        })
                
                # Locations
                if "location" in result:
                    loc = result["location"]
                    if isinstance(loc, (list, tuple)) and len(loc) >= 2:
                        points.append({
                            "lat": float(loc[0]),
                            "lon": float(loc[1]),
                            "label": "📍 Location"
                        })
    
    # Parse coordinates from text - improved pattern matching
    text = str(agent_output)
    
    # Pattern 1: (lat, lon) or [lat, lon]
    coord_pattern1 = r'[\[\(]?\s*([+-]?\d+\.?\d+)\s*[,]\s*([+-]?\d+\.?\d+)\s*[\]\)]?'
    matches1 = re.findall(coord_pattern1, text)
    
    # Pattern 2: "lat: X, lon: Y" or "latitude: X, longitude: Y"
    coord_pattern2 = r'(?:lat|latitude)[:\s]+([+-]?\d+\.?\d+).*?(?:lon|lng|longitude)[:\s]+([+-]?\d+\.?\d+)'
    matches2 = re.findall(coord_pattern2, text, re.IGNORECASE)
    
    # Pattern 3: Numbers that look like coordinates (pairs of numbers)
    coord_pattern3 = r'\b(\d{1,2}\.\d+)[,\s]+(\d{1,3}\.\d+)\b'
    matches3 = re.findall(coord_pattern3, text)
    
    all_matches = matches1 + matches2 + matches3
    
    for match in all_matches[:20]:  # Limit to 20 matches
        try:
            lat, lon = float(match[0]), float(match[1])
            # Validate coordinates
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                # Check if we already have this point (within 0.01 degrees)
                if not any(abs(p['lat'] - lat) < 0.01 and abs(p['lon'] - lon) < 0.01 for p in points):
                    points.append({
                        "lat": lat,
                        "lon": lon,
                        "label": f"📍 ({lat:.2f}, {lon:.2f})"
                    })
        except:
            pass
    
    # Add markers
    if points:
        for p in points:
            label = p.get('label', 'Location').replace('"', '\\"').replace('\n', ' ')
            html += f"""
            L.marker([{p['lat']}, {p['lon']}]).addTo(map)
                .bindPopup("{label}");
            """
        # Fit bounds
        lats = [p['lat'] for p in points]
        lons = [p['lon'] for p in points]
        html += f"map.fitBounds([[{min(lats)}, {min(lons)}], [{max(lats)}, {max(lons)}]]);"
    else:
        # Show a message if no points found
        html += """
        L.marker([20, 0]).addTo(map)
            .bindPopup("No locations found. Try asking about specific coordinates or locations!");
        """
    
    # Add lines
    for line in lines:
        coords = line["coords"]
        color = line.get("color", "red")
        html += f"animateLine({json.dumps(coords)}, '{color}');"
    
    # Add circles
    for c in circles:
        html += f"""
        L.circle([{c['lat']}, {c['lon']}], {{
            radius: {c['radius'] * 1000},
            color: "#3498db",
            fillColor: "#3498db",
            fillOpacity: 0.2,
            weight: 2
        }}).addTo(map).bindPopup("Coverage: {c['radius']}km");
        """
    
    html += "</script>"
    return html


def process_query(message, history):
    """Process user query and update all components."""
    if not message.strip():
        return history, ""
    
    # Get response
    output, tool_results = ask_agent(message)
    
    # Build map
    map_html = build_leaflet_map(output, tool_results)
    
    # Update chat history
    history = history + [(message, output)]
    
    return history, "", map_html


def clear_all():
    """Clear all components."""
    default_map_html = """
    <div id="map" style="height: 100%; width: 100%; min-height: 600px; border-radius: 8px; border: 2px solid #ddd;"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        L.marker([20, 0]).addTo(map)
            .bindPopup("🗺️ Map cleared. Ask a question to see results!");
    </script>
    """
    return [], "", default_map_html


# Example queries
examples = [
    "List submarine cables near 10, 20",
    "Find nearby base stations around 5, 5",
    "What is the signal strength at 1.1, 2.2?",
    "Show me the cable route between France and Brazil",
    "Find landing stations in Japan",
    "What's the coverage area for base stations near 10, 10 with 5km radius?"
]


# Create impressive Gradio interface
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="🌍 Advanced MCP Map Assistant",
    css="""
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    """
) as demo:
    
    # Header
    gr.HTML("""
    <div class="main-header">
        <h1>🌍 Advanced MCP Map Assistant</h1>
        <p>Interactive AI-powered mapping for submarine cables and base station coverage</p>
    </div>
    """)
    
    with gr.Row():
        # Left Column - Chat and Input
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(
                label="💬 Conversation",
                height=400,
                show_label=True,
                avatar_images=(None, "🤖")
            )
            
            with gr.Row():
                user_input = gr.Textbox(
                    label="Ask your question",
                    placeholder="e.g., 'Find base stations near 10, 10' or 'Show cables near Japan'",
                    scale=4,
                    show_label=False
                )
                submit_btn = gr.Button("🚀 Send", scale=1, variant="primary")
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                examples_btn = gr.Button("💡 Examples", variant="secondary")
            
            gr.Examples(
                examples=examples,
                inputs=user_input,
                label="💡 Try these examples:"
            )
        
        # Right Column - Map
        with gr.Column(scale=1):
            # Default map HTML - always show a map
            default_map_html = """
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

            <div id="map" style="height: 600px; width: 100%; border-radius: 8px; border: 2px solid #ddd;"></div>

            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

            <script>
            window.onload = function () {
                var map = L.map('map').setView([20, 0], 2);
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                L.marker([20, 0]).addTo(map)
                    .bindPopup("🗺️ Interactive Map<br>Ask a question to see locations, cables, and coverage areas!");
            }
            </script>
            """

            map_display = gr.HTML(
                value=default_map_html,
                label="🗺️ Interactive Map Visualization",
                 elem_id="map_html",
            )
            
            gr.Markdown("""
            ### 📊 Features:
            - **📍 Markers**: Base stations and landing points
            - **🔴 Routes**: Animated cable paths
            - **🔵 Coverage**: Signal coverage areas
            - **🔍 Auto-zoom**: Automatically fits to show all results
            """)
    
    # Status bar
    with gr.Row():
        status = gr.Markdown("✅ **Status**: Ready to answer your questions!")
    
    # Event handlers
    submit_btn.click(
        fn=process_query,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, map_display]
    )
    
    user_input.submit(
        fn=process_query,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, map_display]
    )
    
    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[chatbot, user_input, map_display]
    )


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", inbrowser=True)
