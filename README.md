# 🌍 MCP Map Project - AI-Powered Geographic Intelligence System

An advanced AI agent system that leverages Claude AI to intelligently query and visualize submarine cable networks and cellular base station infrastructure through a beautiful web interface.

## 📋 Project Overview

This project implements a **Model Context Protocol (MCP) compliant agent system** that:
- Uses OpenAI's Agents SDK with Claude AI
- Provides 10 specialized tools for geographic data queries
- Visualizes results on interactive maps
- Offers both CLI and web-based interfaces

### Two Map Servers

1. **Submarine Cables Server** 🌊
   - Landing stations database
   - Cable route planning
   - Latency estimation
   - Outage risk assessment

2. **Base Station Coverage Server** 📡
   - Coverage analysis
   - Signal strength mapping
   - Handover simulation
   - Capacity planning

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API Key
- Virtual environment (recommended)

### Installation

1. **Clone or navigate to the project:**
```bash
git clone https://github.com/alineFhassan/EECE798S_C5.git
```

2. **Create and activate virtual environment:**

**Command Prompt (CMD):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```bash
# In project root, create .env with:
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

#### 🖥️ Web Interface (Recommended)
```bash
python app.py
```
- Opens Gradio web UI at `http://localhost:7860`
- Interactive map with markers, routes, and coverage areas
- Beautiful chat interface with example queries

#### 💻 Command Line Interface
```bash
python main.py
```
- Interactive CLI mode
- Type queries and get instant responses
- Type `quit` or `exit` to exit

---

## 🛠️ Architecture

### Project Structure

```
mcp_map_project/
├── main.py                    # CLI entry point
├── app.py                     # Gradio web UI
├── models.py                  # Dataclasses (MCP conventions)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── README.md                  # This file
│
├── servers/                   # Map server implementations
│   ├── submarine_server.py    # Submarine cables server
│   └── basestation_server.py  # Base station coverage server
│
└── tests/                     # Unit tests
    ├── test_submarine_server.py
    ├── test_basestation_server.py
    ├── test_agent_routing.py
    └── conftest.py
```

### Data Flow

```
User Query
    ↓
Agent (Claude AI with @function_tool decorators)
    ↓
Tool Selection & Execution
    ↓
Server Method Execution
    ↓
Structured Response (Dataclasses)
    ↓
Agent Natural Language Answer
    ↓
Map Visualization + Chat Display
```

---

## 🔧 Features

### 10 Agent Tools

#### Submarine Cable Tools
1. **locate_landing_station**(country) → LandingStationResponse
   - Find landing stations by country

2. **cable_route_between**(country_a, country_b) → CableRoute
   - Get submarine cable routes between countries

3. **list_cables_near**(lat, lon, radius_km) → List[str]
   - Find cables near geographic coordinates

4. **cable_latency_estimate**(country_a, country_b) → CableLatencyResponse
   - Estimate latency between countries

5. **cable_outage_risk**(lat, lon) → CableOutageRiskResponse
   - Assess outage risk at ocean coordinates

#### Base Station Tools
6. **nearest_basestations**(lat, lon, radius_km) → BaseStationResponse
   - Find nearby cellular base stations

7. **coverage_strength_at**(lat, lon) → CoverageStrengthResponse
   - Get signal strength at specific location

8. **propose_new_station**(lat, lon, required_radius) → ProposedStation
   - Suggest new base station locations

9. **stations_with_capacity**(min_capacity) → BaseStationResponse
   - Find stations meeting capacity requirements

10. **handover_path**(start_lat, start_lon, end_lat, end_lon) → HandoverPathResponse
    - Simulate mobile handover along route

### Map Visualization

- **Interactive Leaflet.js maps**
- **Real-time marker placement**
- **Animated cable routes** with polylines
- **Coverage area circles** with radius indicators
- **Auto-zoom to results**
- **OpenStreetMap tiles**

### UI/UX

- Beautiful gradient header
- Example queries for users
- Responsive two-column layout
- Chat history display
- Clear button to reset

---

## 📖 Example Queries

### Submarine Cable Queries
```
"Find landing stations in Japan"
"Show me the cable route between France and Brazil"
"List submarine cables near 10, 20"
"What's the latency between US and UK?"
"What's the outage risk at 35, 139?"
```

### Base Station Queries
```
"Find nearby base stations around 5, 5"
"What is the signal strength at 1.1, 2.2?"
"Find stations with at least 1500 capacity"
"Propose a new base station at 10, 10 with 5km radius"
"Show handover path from 1, 1 to 2, 2"
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_submarine_server.py -v
pytest tests/test_basestation_server.py -v
pytest tests/test_agent_routing.py -v
```

### Test Coverage
- ✅ Server method implementations
- ✅ Agent tool routing
- ✅ Response data types
- ✅ Coordinate validation

---

## 🔌 Server Implementation Details

### Submarine Cables Server
**Location:** `servers/submarine_server.py`

Mock implementations of 5 operations:
- Landing station lookup
- Cable routing
- Proximate cable search
- Latency calculation
- Outage risk assessment

### Base Station Coverage Server
**Location:** `servers/basestation_server.py`

Mock implementations of 5 operations:
- Nearest station search
- Coverage strength analysis
- New station proposal
- Capacity filtering
- Handover simulation

> **Note:** Currently using mock data. Can be extended to use real APIs (OpenCellID, TeleGeography, etc.)

---

## 📊 Models & MCP Conventions

All request/response objects follow MCP conventions using Python dataclasses:

**Location:** `models.py`

### Submarine Cable Models
- `LandingStation`
- `LandingStationResponse`
- `CableRoute`
- `CableLatencyResponse`
- `CableOutageRiskResponse`

### Base Station Models
- `BaseStation`
- `BaseStationResponse`
- `CoverageStrengthResponse`
- `ProposedStation`
- `HandoverEvent`
- `HandoverPathResponse`

---

## 🔐 Security

- ✅ API keys managed via `.env` file
- ✅ Never commit `.env` to version control
- ✅ Environment variable validation
- ✅ Type safety with dataclasses

---

## 📚 Dependencies

- `agents` - OpenAI Agents SDK
- `gradio` - Web UI framework
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework

See `requirements.txt` for exact versions.

---

## 🤝 How It Works

### Agent Architecture

1. **Tool Registration**
   ```python
   @function_tool
   def nearest_basestations(lat: float, lon: float, radius_km: float) -> BaseStationResponse:
       return base._nearest_basestations_impl(lat, lon, radius_km)
   ```

2. **Agent Creation**
   ```python
   agent = Agent(
       name="MapAssistant",
       instructions="...",
       tools=[tool1, tool2, ...]
   )
   ```

3. **Query Execution**
   ```python
   result = await Runner.run(agent, input="Find base stations near 10, 10")
   ```

4. **Agent Flow**
   - Understands user query
   - Selects appropriate tool(s)
   - Executes tool with parameters
   - Generates natural language response
   - Coordinates extracted for map visualization

---

## 🚀 Future Enhancements

- [ ] Real API integration (OpenCellID, TeleGeography)
- [ ] Database backend (PostgreSQL with GIS)
- [ ] Advanced filtering and analytics
- [ ] Historical data tracking
- [ ] Real-time updates
- [ ] Multi-language support
- [ ] Mobile responsive design
- [ ] Export capabilities (GeoJSON, KML)

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💻 Development

### Create New Tool

1. Add method to server class in `servers/`
2. Create response model in `models.py`
3. Register tool with `@function_tool` in `main.py` and `app.py`
4. Write unit tests in `tests/`

### Debug Mode

Set `DEBUG=true` in `.env` for verbose logging.

---

## ❓ Troubleshooting

### "OPENAI_API_KEY not found"
- Create `.env` file: `OPENAI_API_KEY=sk-...`
- Or set system environment variable

### "ModuleNotFoundError"
- Activate venv: `venv\Scripts\activate.bat`
- Install deps: `pip install -r requirements.txt`

### Tests failing
- Ensure all server methods have `_impl` suffix
- Check `models.py` is in root folder
- Run: `pytest tests/ -v` for details

### Gradio port already in use
- Change port: `demo.launch(server_name="0.0.0.0", server_port=7861)`

---
