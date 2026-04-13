"""Tuition utility tests."""

from src.agents.finance.tuition_utils import is_personal_query


def test_is_personal_query_treats_installment_policy_question_as_non_personal():
    assert is_personal_query("Taksitle odeyebilir miyim?") is False


def test_is_personal_query_keeps_real_personal_balance_question_personal():
    assert is_personal_query("Harc borcum var mi?") is True
