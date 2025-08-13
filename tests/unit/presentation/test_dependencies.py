from types import SimpleNamespace

from src.presentation.api.dependencies import get_dcf_services


class StubFactory:
    def create_dcf_assumptions_service(self):
        return SimpleNamespace(name="dcf_assumptions_service")

    def create_initial_numbers_service(self):
        return SimpleNamespace(name="initial_numbers_service")

    def create_cash_flow_projection_service(self):
        return SimpleNamespace(name="cash_flow_projection_service")

    def create_financial_metrics_service(self):
        return SimpleNamespace(name="financial_metrics_service")


def test_get_dcf_services_mapping(monkeypatch):
    from src.application.factories import service_factory as sf

    monkeypatch.setattr(sf, "get_service_factory", lambda: StubFactory())

    services = get_dcf_services()
    assert set(services.keys()) == {
        "dcf_assumptions",
        "initial_numbers",
        "cash_flow_projection",
        "financial_metrics",
    }
    assert services["dcf_assumptions"] is not None
