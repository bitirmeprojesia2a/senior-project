from __future__ import annotations

import pytest

from scripts import audit_shadow_trace_structural as structural_audit
from scripts import run_shadow_trace_golden as golden


def test_shadow_trace_golden_defaults_keep_warmup_and_retry_off() -> None:
    args = golden.build_arg_parser().parse_args([])

    assert args.warmup_mode == "none"
    assert args.provider_retry_count == 0
    assert args.provider_retry_backoff == 0.0


def test_shadow_trace_golden_parses_warmup_and_retry_flags() -> None:
    args = golden.build_arg_parser().parse_args(
        [
            "--warmup-mode",
            "full",
            "--provider-retry-count",
            "1",
            "--provider-retry-backoff",
            "8",
        ]
    )

    assert args.warmup_mode == "full"
    assert args.provider_retry_count == 1
    assert args.provider_retry_backoff == 8.0


@pytest.mark.asyncio
async def test_shadow_trace_golden_warmup_failure_is_reported(monkeypatch) -> None:
    def fail_prewarm(*args, **kwargs):
        raise RuntimeError("warmup boom")

    monkeypatch.setattr(golden.HybridRetriever, "prewarm", fail_prewarm)

    summary = await golden._run_warmup("retrieval", llm_profile="balanced")

    assert summary["mode"] == "retrieval"
    assert summary["retrieval"]["enabled"] is True
    assert summary["retrieval"]["status"] == "error"
    assert summary["retrieval"]["error_type"] == "RuntimeError"
    assert "warmup boom" in summary["retrieval"]["error"]


def test_shadow_trace_golden_provider_error_stats_classifies_known_failures() -> None:
    rows = [
        {
            "llm_usage": [
                {
                    "status": "error",
                    "provider_label": "groq",
                    "error_message": "HTTP hatasi (429): rate_limit_exceeded",
                },
                {
                    "status": "error",
                    "provider_label": "groq",
                    "error_message": "json_validate_failed: Failed to generate JSON",
                },
            ]
        }
    ]

    stats = golden._provider_error_stats(rows)

    assert stats["total"] == 2
    assert stats["retryable"] == 2
    assert stats["by_provider"] == {"groq": 2}
    assert stats["by_reason"]["rate_limit"] == 1
    assert stats["by_reason"]["json_validate_failed"] == 1


def test_shadow_trace_golden_provider_error_stats_includes_retry_attempts() -> None:
    rows = [
        {
            "llm_usage": [],
            "provider_retry_attempts": [
                {
                    "retryable_provider_error": True,
                    "provider_errors": [
                        {
                            "provider": "groq",
                            "reason": "rate_limit",
                        }
                    ],
                }
            ],
        }
    ]

    stats = golden._provider_error_stats(rows)

    assert stats["total"] == 1
    assert stats["retryable"] == 1
    assert stats["by_provider"] == {"groq": 1}
    assert stats["by_reason"] == {"rate_limit": 1}


def test_shadow_trace_golden_provider_error_stats_can_split_final_and_retry() -> None:
    rows = [
        {
            "llm_usage": [
                {
                    "status": "error",
                    "provider_label": "groq",
                    "error_message": "timeout",
                }
            ],
            "provider_retry_attempts": [
                {
                    "retryable_provider_error": True,
                    "provider_errors": [{"provider": "groq", "reason": "rate_limit"}],
                }
            ],
        }
    ]

    final_stats = golden._provider_error_stats(rows, include_retry_attempts=False)
    retry_stats = golden._provider_error_stats(rows, include_llm_usage=False)

    assert final_stats["total"] == 1
    assert final_stats["by_reason"] == {"timeout": 1}
    assert retry_stats["total"] == 1
    assert retry_stats["by_reason"] == {"rate_limit": 1}


def test_shadow_trace_golden_final_retryable_provider_error_is_check() -> None:
    row = {
        "expected_owner": "academic_calendar",
        "trace_owner": "academic_calendar",
        "expected_capability": "calendar.academic_date",
        "trace_capability": "calendar.academic_date",
        "answer_validation": {"status": "pass"},
        "llm_usage": [
            {
                "status": "error",
                "provider_label": "groq",
                "error_message": "HTTP hatasi (429): rate_limit_exceeded",
            }
        ],
    }

    assert golden._structural_issues(row) == ["provider_retryable_error_seen"]
    assert golden._row_status(row) == "CHECK"
    assert golden._provider_warning_summary(row) == "final_retryable=1"


def test_shadow_trace_golden_retry_history_provider_error_is_warning_only() -> None:
    row = {
        "expected_owner": "academic_calendar",
        "trace_owner": "academic_calendar",
        "expected_capability": "calendar.academic_date",
        "trace_capability": "calendar.academic_date",
        "answer_validation": {"status": "pass"},
        "llm_usage": [],
        "provider_retry_attempts": [
            {
                "provider_errors": [
                    {"provider": "groq", "role": "routing", "reason": "rate_limit"}
                ]
            }
        ],
    }

    assert golden._structural_issues(row) == []
    assert golden._row_status(row) == "OK"
    assert golden._provider_warning_summary(row) == "retry_history=1"


def test_shadow_trace_golden_non_retryable_provider_error_stays_structural() -> None:
    row = {
        "expected_owner": "academic_calendar",
        "trace_owner": "academic_calendar",
        "expected_capability": "calendar.academic_date",
        "trace_capability": "calendar.academic_date",
        "answer_validation": {"status": "pass"},
        "llm_usage": [
            {
                "status": "error",
                "provider_label": "groq",
                "error_message": "permission denied",
            }
        ],
    }

    assert golden._structural_issues(row) == ["provider_error_seen"]
    assert golden._row_status(row) == "CHECK"


def test_shadow_trace_golden_answer_quality_shadow_flags_foreign_tokens() -> None:
    result = golden._answer_quality_shadow(
        "Ogrenci isleri departamento gore basvuru yapabilirsiniz. alumnoğuz devam eder."
    )

    assert result["status"] == "check"
    assert result["foreign_token_shadow"] is True
    assert "departamento" in result["bad_tokens"]


def test_shadow_trace_golden_answer_quality_ignores_report_metadata_tokens() -> None:
    result = golden._answer_quality_shadow(
        "Final sinavlari Ocak ayinda baslar.\n\n---\nUretim Turu:\n- Routing: direct"
    )

    assert result["bad_tokens"] == []
    assert result["foreign_token_shadow"] is False


def test_shadow_trace_golden_expands_follow_up_dependencies() -> None:
    selected = [case for case in golden.GOLDEN_CASES if case.id in {"GT01", "GT12"}]

    expanded = golden._expand_case_dependencies(selected)

    assert [case.id for case in expanded] == ["GT01", "GT11", "GT12"]


def test_shadow_trace_golden_llm_token_stats_summarizes_usage() -> None:
    rows = [
        {
            "llm_usage": [
                {
                    "model_role": "routing",
                    "prompt_chars": 20,
                    "system_chars": 4,
                    "estimated_input_tokens": 6,
                },
                {
                    "model_role": "global_synthesis",
                    "prompt_chars": 100,
                    "system_chars": 20,
                    "estimated_input_tokens": 30,
                },
            ]
        }
    ]

    stats = golden._llm_token_stats(rows)

    assert stats["calls_with_estimate"] == 2
    assert stats["estimated_input_tokens"] == 36
    assert stats["prompt_chars"] == 120
    assert stats["system_chars"] == 24
    assert stats["by_role"]["routing"]["estimated_input_tokens"] == 6
    assert stats["by_role"]["global_synthesis"]["estimated_input_tokens"] == 30


def test_shadow_trace_golden_key_distribution_summarizes_fingerprints() -> None:
    rows = [
        {
            "llm_usage": [
                {
                    "provider_label": "groq",
                    "api_key_fingerprint": "key-a",
                    "api_key_count": 3,
                },
                {
                    "provider_label": "groq",
                    "api_key_fingerprint": "key-b",
                    "api_key_count": 3,
                    "provider_org_fingerprint": "org-a",
                },
            ]
        }
    ]

    stats = golden._llm_key_distribution(rows)

    assert stats["by_provider"]["groq"]["calls"] == 2
    assert stats["by_provider"]["groq"]["key_count"] == 3
    assert stats["by_provider"]["groq"]["by_fingerprint"] == {"key-a": 1, "key-b": 1}
    assert stats["provider_org_fingerprints"] == {"org-a": 1}


def test_shadow_trace_golden_row_status_checks_structural_contract() -> None:
    row = {
        "expected_owner": "student_affairs_policy",
        "trace_owner": "student_affairs_policy",
        "expected_capability": "student_affairs.policy_lookup",
        "trace_capability": "student_affairs.policy_lookup",
        "expected_primary_department": "student_affairs",
        "expected_primary_specialist": "registration_agent",
        "trace_departments": ["academic_programs"],
        "trace_selected_specialists": ["regulation_agent"],
        "trace_specialist_selections": [
            {
                "department": "academic_programs",
                "selected_agent_id": "regulation_agent",
            }
        ],
        "trace_response_filter": {
            "kept": [
                {
                    "department": "academic_programs",
                    "source_owner_primary": False,
                    "has_source_owner_evidence": True,
                }
            ]
        },
        "llm_usage": [],
        "answer_validation": {"status": "pass"},
    }

    assert golden._row_status(row) == "CHECK"
    assert golden._structural_issues(row) == [
        "primary_department expected=student_affairs actual=academic_programs",
        "primary_specialist expected=registration_agent actual=regulation_agent",
    ]


def test_shadow_trace_golden_structural_contract_accepts_primary_evidence_branch() -> None:
    row = {
        "expected_owner": "student_affairs_policy",
        "trace_owner": "student_affairs_policy",
        "expected_capability": "student_affairs.policy_lookup",
        "trace_capability": "student_affairs.policy_lookup",
        "expected_primary_department": "student_affairs",
        "expected_primary_specialist": "registration_agent",
        "trace_departments": ["academic_programs"],
        "trace_selected_specialists": ["registration_agent", "regulation_agent"],
        "trace_specialist_selections": [
            {
                "department": "student_affairs",
                "selected_agent_id": "registration_agent",
            },
            {
                "department": "academic_programs",
                "selected_agent_id": "regulation_agent",
            },
        ],
        "trace_response_filter": {
            "kept": [
                {
                    "department": "student_affairs",
                    "source_owner_primary": True,
                    "has_source_owner_evidence": True,
                },
                {
                    "department": "academic_programs",
                    "source_owner_primary": False,
                    "has_source_owner_evidence": True,
                },
            ]
        },
        "llm_usage": [],
        "answer_validation": {"status": "pass"},
    }

    assert golden._structural_issues(row) == []
    assert golden._row_status(row) == "OK"


def test_shadow_trace_golden_checks_primary_branch_timeout() -> None:
    row = {
        "expected_owner": "student_affairs_policy",
        "trace_owner": "student_affairs_policy",
        "expected_capability": "student_affairs.policy_lookup",
        "trace_capability": "student_affairs.policy_lookup",
        "expected_primary_department": "student_affairs",
        "expected_primary_specialist": "registration_agent",
        "trace_departments": ["student_affairs", "academic_programs"],
        "trace_selected_specialists": ["registration_agent", "regulation_agent"],
        "trace_specialist_selections": [
            {
                "department": "student_affairs",
                "selected_agent_id": "registration_agent",
            }
        ],
        "trace_response_filter": {
            "kept": [
                {
                    "department": "student_affairs",
                    "success": False,
                    "error": "a2a_specialist_transport_timeout",
                    "source_owner_primary": True,
                    "has_source_owner_evidence": False,
                },
                {
                    "department": "academic_programs",
                    "success": True,
                    "source_owner_primary": False,
                    "has_source_owner_evidence": True,
                },
            ]
        },
        "llm_usage": [],
        "answer_validation": {"status": "pass"},
    }

    assert golden._structural_issues(row) == [
        "primary_branch_timeout department=student_affairs error=a2a_specialist_transport_timeout"
    ]
    assert golden._row_status(row) == "CHECK"


def test_shadow_trace_golden_checks_missing_specialist_selector_diagnostics() -> None:
    row = {
        "expected_owner": "student_affairs_policy",
        "trace_owner": "student_affairs_policy",
        "expected_capability": "student_affairs.policy_lookup",
        "trace_capability": "student_affairs.policy_lookup",
        "expected_primary_department": "student_affairs",
        "expected_primary_specialist": "registration_agent",
        "trace_departments": ["student_affairs", "academic_programs"],
        "trace_selected_specialists": ["registration_agent", "regulation_agent"],
        "trace_specialist_selections": [
            {
                "schema": "omu.specialist_selection.legacy",
                "department": "student_affairs",
                "selected_agent_id": "registration_agent",
                "selected_by": "unknown",
                "reason": "response_metadata_without_selector_diagnostics",
            }
        ],
        "trace_response_filter": {
            "kept": [
                {
                    "department": "student_affairs",
                    "source_owner_primary": True,
                    "has_source_owner_evidence": True,
                }
            ]
        },
        "llm_usage": [],
        "answer_validation": {"status": "pass"},
    }

    assert golden._structural_issues(row) == ["specialist_selector_diagnostics_missing"]
    assert golden._row_status(row) == "CHECK"


def test_shadow_trace_golden_row_status_checks_answer_coverage_shadow() -> None:
    row = {
        "expected_owner": "student_affairs_policy",
        "trace_owner": "student_affairs_policy",
        "answer_validation": {"status": "pass"},
        "answer_coverage": {
            "mode": "shadow",
            "status": "check",
            "expected_facet": "application_process",
        },
        "llm_usage": [],
    }

    assert golden._row_status(row) == "CHECK"


def test_shadow_trace_golden_row_status_checks_value_conflict_shadow() -> None:
    row = {
        "expected_owner": "student_affairs_policy",
        "trace_owner": "student_affairs_policy",
        "answer_validation": {"status": "pass"},
        "answer_coverage": {"status": "pass"},
        "answer_value_conflict": {
            "mode": "shadow",
            "status": "check",
            "reason": "multiple_competing_threshold_values",
            "primary_answer_value": "2,00",
            "competing_values": ["3,00"],
        },
        "llm_usage": [],
    }

    assert golden._row_status(row) == "CHECK"


def test_shadow_trace_offline_structural_audit_reclassifies_archived_rows() -> None:
    rows = structural_audit._audit_rows(
        [
            {
                "id": "GT12",
                "expected_owner": "student_affairs_policy",
                "trace_owner": "student_affairs_policy",
                "expected_capability": "student_affairs.policy_lookup",
                "trace_capability": "student_affairs.policy_lookup",
                "expected_primary_department": "student_affairs",
                "expected_primary_specialist": "registration_agent",
                "trace_departments": ["academic_programs"],
                "trace_selected_specialists": ["regulation_agent"],
                "trace_specialist_selections": [
                    {
                        "department": "academic_programs",
                        "selected_agent_id": "regulation_agent",
                    }
                ],
                "answer_validation": {"status": "pass"},
                "llm_usage": [],
            }
        ]
    )

    assert rows[0]["structural_status"] == "CHECK"
    assert rows[0]["structural_issues"] == [
        "primary_department expected=student_affairs actual=academic_programs",
        "primary_specialist expected=registration_agent actual=regulation_agent",
    ]


def test_shadow_trace_offline_audit_recomputes_value_conflict_from_preview() -> None:
    rows = structural_audit._audit_rows(
        [
            {
                "id": "GT12",
                "query": "Peki not ortalamasi kac olmali?",
                "expected_owner": "student_affairs_policy",
                "trace_owner": "student_affairs_policy",
                "expected_capability": "student_affairs.policy_lookup",
                "trace_capability": "student_affairs.policy_lookup",
                "expected_primary_department": "student_affairs",
                "expected_primary_specialist": "registration_agent",
                "trace_departments": ["student_affairs"],
                "trace_selected_specialists": ["registration_agent"],
                "trace_response_filter": {
                    "kept": [
                        {
                            "department": "student_affairs",
                            "source_owner_primary": True,
                            "has_source_owner_evidence": True,
                        }
                    ]
                },
                "answer_preview": "Not ortalamasi en az 2,00 olmalidir. CAP icin 3,00 gerekebilir.",
                "answer_validation": {"status": "pass"},
                "answer_coverage": {"status": "pass"},
                "llm_usage": [],
            }
        ]
    )

    assert rows[0]["answer_value_conflict"]["status"] == "check"
    assert rows[0]["structural_status"] == "CHECK"
