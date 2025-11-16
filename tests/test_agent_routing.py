import asyncio
from agents import Runner
from main import build_agent

def test_agent_tool_routing():
    agent = build_agent()
    
    # Helper function to run async queries
    def run_query(query):
        # Runner.run() is a static async method
        result = asyncio.run(Runner.run(agent, input=query))
        return result.final_output

    # Query about submarine cables
    response1 = run_query("List submarine cables near 10,20")
    assert "cables" in str(response1).lower()

    # Query about base stations
    response2 = run_query("Find nearby base stations around 5,5")
    assert "stations" in str(response2).lower()

    # Query about coverage
    response3 = run_query("What is the signal strength at 1.1,2.2?")
    assert "signal" in str(response3).lower()
