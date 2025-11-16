from servers.submarine_server import SubmarineCablesServer

def test_locate_landing_station():
    server = SubmarineCablesServer()
    result = server._locate_landing_station_impl(country="Japan")
    assert "landing_stations" in result
    assert isinstance(result["landing_stations"], list)

def test_cable_route_between():
    server = SubmarineCablesServer()
    result = server._cable_route_between_impl("France", "Brazil")
    assert result["from"] == "France"
    assert result["to"] == "Brazil"
    assert "distance_km" in result

def test_list_cables_near():
    server = SubmarineCablesServer()
    result = server._list_cables_near_impl(10, 20, 100)
    assert "cables" in result
    assert isinstance(result["cables"], list)

def test_cable_latency_estimate():
    server = SubmarineCablesServer()
    result = server._cable_latency_estimate_impl("USA", "UK")
    assert "estimated_latency_ms" in result
    assert result["estimated_latency_ms"] > 0

def test_cable_outage_risk():
    server = SubmarineCablesServer()
    result = server._cable_outage_risk_impl(5.0, 8.0)
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 1
