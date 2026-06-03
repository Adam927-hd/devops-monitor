from api.metrics import get_system_metrics


def test_metrics_keys():
    data = get_system_metrics()
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data


def test_metrics_ranges():
    data = get_system_metrics()
    assert 0 <= data["cpu_percent"] <= 100
    assert 0 <= data["memory_percent"] <= 100
    assert 0 <= data["disk_percent"] <= 100
