"""The shot-duration floor must reach the writer before first draft and again on T12.

These tests use the actual composing/repair request builders with a capturing
backend: no LLM or GPU is required. Shot counts are still the user's choice.
"""
from __future__ import annotations

from types import SimpleNamespace

from h3ir.draft import deterministic_draft
from h3ir.models import Brief, Finding, Mode
from h3ir.plan import ProfileOptions
from h3ir.prose import compose_brief, fix_with_findings, shot_timing_contract


class Capture:
    def __init__(self):
        self.messages = []

    def chat(self, messages, **kwargs):
        self.messages.append(messages)
        return SimpleNamespace(content="test response")

    @property
    def last_ask(self):
        return self.messages[-1][-1]["content"]


def _compose(shots=None):
    brief = Brief(intent="A basketball player takes the winning shot", seconds=15.0,
                  shots=shots)
    plan = deterministic_draft(brief, Mode.T2VA, {}, opts=ProfileOptions())
    backend = Capture()
    compose_brief(backend, brief, plan.subjects, {}, plan.target, (),
                  mode=Mode.T2VA, prompt_name="compose_base.v1.txt")
    return backend.last_ask


def test_timing_uses_snapped_duration_and_last_cut_rounds_down_to_millisecond():
    contract = shot_timing_contract(362 / 24)
    assert "15.083s" in contract
    assert "1.200s" in contract
    assert "00:13.883" in contract
    assert "INCLUDING the last" in contract
    assert "zero-duration final shot" in contract


def test_last_cut_timestamp_formats_minutes_correctly():
    contract = shot_timing_contract(75.083333)
    assert "01:13.883" in contract


def test_initial_auto_ask_includes_floor_and_allows_fewer_shots():
    ask = _compose()
    assert "Shot timing contract:" in ask
    assert "00:13.883" in ask
    assert "Shot count is automatic" in ask
    assert "use fewer [Shot N] blocks" in ask


def test_initial_pinned_ask_preserves_pinned_count():
    ask = _compose(shots=5)
    assert "Shot timing contract:" in ask
    assert "The caller pinned exactly 5 shots" in ask
    assert "use fewer [Shot N] blocks" not in ask


def test_t12_feedback_includes_legal_latest_cut_and_allows_merge_only_for_auto():
    backend = Capture()
    findings = [Finding("T12-cut-inside-the-floor", "ERROR",
                        "last shot starts at 15.083s")]
    fix_with_findings(backend, "initial brief", findings, duration_s=362/24,
                      pinned_shots=None)
    ask = backend.last_ask
    assert "00:13.883" in ask
    assert "merge the too-short shot" in ask
    assert "without deleting its action" in ask
    assert "Keep your shots," not in ask
    assert "initial brief" in ask


def test_t12_feedback_keeps_pinned_shot_count_even_if_it_must_move_cuts():
    backend = Capture()
    findings = [Finding("T12-cut-inside-the-floor", "ERROR", "too short")]
    fix_with_findings(backend, "initial brief", findings, duration_s=362/24,
                      pinned_shots=5)
    ask = backend.last_ask
    assert "The caller pinned exactly 5 shots" in ask
    assert "Keep your shots," in ask
    assert "merge the too-short shot" not in ask
    assert "00:13.883" in ask


def test_other_corrections_still_use_original_surgical_instruction():
    backend = Capture()
    fix_with_findings(backend, "initial brief",
                      [Finding("L2-undefined-subject", "ERROR", "unknown label")],
                      duration_s=362/24, pinned_shots=None)
    ask = backend.last_ask
    assert "Shot timing contract:" not in ask
    assert "Keep your shots," in ask
    assert "Do not rewrite, do not shorten, do not re-plan" in ask
