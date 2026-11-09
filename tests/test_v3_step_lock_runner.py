from scripts.run_sp2l_v3_offline_step_lock import summarize


def row(reason, ambiguous, realized_r=None, realized_usd=None):
    return {
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_R": realized_r,
        "realized_usd": realized_usd,
    }


def test_summary_separates_ambiguous_from_open_unresolved():
    result = summarize([
        row("SL", False, -1.0, -1.0),
        row("STEP_LOCK_SL", False, 1.0, 1.0),
        row("M1_GAP_WHILE_OPEN", True),
        row("OPEN_OR_UNRESOLVED", False),
    ])
    assert result["signals"] == 4
    assert result["decisive"] == 2
    assert result["ambiguous"] == 1
    assert result["open_unresolved"] == 1
    assert result["unresolved_total"] == 2
    assert result["net_R"] == 0.0
    assert result["gross_usd"] == 0.0
