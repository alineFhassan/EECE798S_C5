from servers.basestation_server import BaseStationCoverageServer

def test_nearest_basestations():
    server = BaseStationCoverageServer()
    result = server._nearest_basestations_impl(10, 10, 5)
    assert "stations" in result
    assert isinstance(result["stations"], list)

def test_coverage_strength_at():
    server = BaseStationCoverageServer()
    result = server._coverage_strength_at_impl(1.1, 2.2)
    assert "signal_strength" in result

def test_propose_new_station():
    server = BaseStationCoverageServer()
    result = server._propose_new_station_impl(50, 30, 2)
    assert "suggested_location" in result

def test_stations_with_capacity():
    server = BaseStationCoverageServer()
    result = server._stations_with_capacity_impl(400)
    assert len(result["filtered_stations"]) >= 1

def test_handover_path():
    server = BaseStationCoverageServer()
    result = server._handover_path_impl(0, 0, 1, 1)
    assert "handover_sequence" in result
    assert isinstance(result["handover_sequence"], list)
