from divyadrishti.reasoning import ChartData, Evidence, PlanetPosition, ReasoningTrace


def test_planet_position():
    pos = PlanetPosition(house=7, sign="Libra")
    assert pos.house == 7
    assert pos.sign == "Libra"


def test_chart_data_active_fields():
    chart = ChartData(
        planets={
            "Jupiter": PlanetPosition(house=7, sign="Libra"),
            "Saturn": PlanetPosition(house=7, sign="Libra"),
        }
    )
    assert chart.active_houses == [7]
    assert "Jupiter" in chart.active_planets


def test_evidence_model():
    ev = Evidence(
        rule_id="BPHS_7TH_001",
        source="BPHS",
        conditions=["Jupiter in 7th"],
        matched_conditions=["Jupiter in 7th"],
        confidence=85.0,
        weight=2.5,
    )
    assert ev.is_supporting() is True


def test_reasoning_trace():
    trace = ReasoningTrace(
        question="Will I marry?",
        chart_data={},
        overall_confidence=80.0,
        reasoning_summary="Summary",
    )
    assert trace.overall_confidence == 80.0
