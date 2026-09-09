from sp2l_trigger_f12 import (
    TriggerForm,
    TriggerState,
    classify_source_neutral,
    is_market_reclaim_trigger,
    trigger_candidates,
)


def test_source_confirmed_trigger_family_is_one_two_three_candle():
    forms = {x.form for x in trigger_candidates()}
    assert TriggerForm.ONE_CANDLE in forms
    assert TriggerForm.TWO_CANDLE in forms
    assert TriggerForm.THREE_CANDLE in forms


def test_key_bar_is_retained_as_candidate_form():
    assert any(x.form is TriggerForm.KEY_BAR for x in trigger_candidates())


def test_no_single_form_is_promoted_to_canonical():
    assert all(classify_source_neutral(x) is TriggerState.CANDIDATE for x in trigger_candidates())


def test_trigger_does_not_become_market_reclaim():
    assert all(not is_market_reclaim_trigger(x) for x in trigger_candidates())
