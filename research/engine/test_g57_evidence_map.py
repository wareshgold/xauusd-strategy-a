from .g57_evidence_map import MAP, all_blockers_are_mapped, source_unique_resolution_exists


def test_all_critical_blockers_are_mapped():
    assert all_blockers_are_mapped()
    assert len(MAP) == 6


def test_g57_does_not_claim_source_unique_geometry():
    assert not source_unique_resolution_exists()


def test_every_mapping_has_source_and_falsification_fixture():
    assert all(item.source_regions for item in MAP)
    assert all(item.falsification_fixtures for item in MAP)
