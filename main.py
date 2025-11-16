import os
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
        """Return landing stations associated with a country."""
        return sub._locate_landing_station_impl(country)
    
    @function_tool
    def cable_route_between(country_a: str, country_b: str) -> CableRoute:
        """Return approximate cable path between two countries."""
        return sub._cable_route_between_impl(country_a, country_b)
    
    @function_tool
    def list_cables_near(lat: float, lon: float, radius_km: float) -> list:
        """List submarine cables near a given location."""
        return sub._list_cables_near_impl(lat, lon, radius_km)
    
    @function_tool
    def cable_latency_estimate(country_a: str, country_b: str) -> CableLatencyResponse:
        """Estimate latency of cable route between countries."""
        return sub._cable_latency_estimate_impl(country_a, country_b)
    
    @function_tool
    def cable_outage_risk(lat: float, lon: float) -> CableOutageRiskResponse:
        """Return outage risk score for an ocean coordinate."""
        return sub._cable_outage_risk_impl(lat, lon)
    
    @function_tool
    def nearest_basestations(lat: float, lon: float, radius_km: float) -> BaseStationResponse:
        """Return nearby base stations."""
        return base._nearest_basestations_impl(lat, lon, radius_km)
    
    @function_tool
    def coverage_strength_at(lat: float, lon: float) -> CoverageStrengthResponse:
        """Return estimated signal strength."""
        return base._coverage_strength_at_impl(lat, lon)
    
    @function_tool
    def propose_new_station(lat: float, lon: float, required_radius: float) -> ProposedStation:
        """Suggest a new base station location."""
        return base._propose_new_station_impl(lat, lon, required_radius)
    
    @function_tool
    def stations_with_capacity(min_capacity: int) -> BaseStationResponse:
        """Return stations meeting minimum capacity."""
        return base._stations_with_capacity_impl(min_capacity)
    
    @function_tool
    def handover_path(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> HandoverPathResponse:
        """Simulate mobile station handover along a route."""
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
        instructions="You are a helpful map assistant that can answer questions about submarine cables and base station coverage.",
        tools=tools
    )

    return agent


async def interactive_mode():
    agent = build_agent()

    print("Map Assistant ready. Type a question or 'quit' to exit.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye.")
            break

        result = await Runner.run(agent, input=user_input)
        print("\nAssistant:", result.final_output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(interactive_mode())
