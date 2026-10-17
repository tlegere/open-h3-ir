"""Versioned creative-direction experiment: wiring and format safety only.

These tests deliberately do NOT grade prose taste. They verify that the
experimental base prompt reaches the real compose request, that the official
base specification remains byte-identical, and that the shipping mode
selection uses the experimental arm. Real quality requires blind text review
and H3 renders against the retained v1 control.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from h3ir.draft import deterministic_draft
from h3ir.models import Brief, Mode, ModeDecision
from h3ir.plan import ProfileOptions
from h3ir.prose import compose_brief, load_prompt


class Capture:
    def __init__(self):
        self.messages = []

    def chat(self, messages, **kwargs):
        self.messages.append(messages)
        return SimpleNamespace(content="ignored by the capturing test")


def test_creative_arm_keeps_the_official_base_spec_and_old_control():
    control = load_prompt("compose_base.v1.txt")
    experiment = load_prompt("compose_base.v2.txt")
    split = "=== END SPECIFICATION ==="

    assert control != experiment
    assert control.split(split)[0] == experiment.split(split)[0]
    assert "three required fields" in experiment
    assert "Exactly three sections" in experiment
    assert "No `subject_definitions`" in experiment
    assert "The exact shot count still belongs to the caller" in experiment
    assert "Static Shot" in experiment
    assert "never contained" in experiment
    assert "Silent self-review before output" in experiment


def test_compose_sends_creative_direction_and_the_existing_timing_contract():
    brief = Brief(intent="An athlete takes a decisive shot", seconds=15.0, shots=4)
    plan = deterministic_draft(brief, Mode.T2VA, {}, opts=ProfileOptions())
    backend = Capture()

    compose_brief(
        backend, brief, plan.subjects, {}, plan.target, (),
        mode=Mode.T2VA, prompt_name="compose_base.v2.txt",
    )

    system, user = backend.messages[-1]
    assert "Compose visual consequences" in system["content"]
    assert "Construct the opening image" in system["content"]
    assert "Earn the cut" in system["content"]
    assert "what enters, leaves, grows, hides" in system["content"]
    assert "Shot timing contract:" in user["content"]
    assert "The caller pinned exactly 4 shots" in user["content"]


def test_real_compiler_picks_v2_for_base_mode_without_changing_the_mode_split(monkeypatch):
    import h3ir.compile as C

    chosen = []

    def capture_composer(backend, brief, subjects, cards, target, labels, **kwargs):
        chosen.append((kwargs["mode"], kwargs["prompt_name"]))
        raise RuntimeError("captured before model invocation")

    class DummyBackend:
        cfg = SimpleNamespace(model="no-llm-needed")

        def require_available(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(C, "compose_brief", capture_composer)
    monkeypatch.setattr(C, "analyse_all", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        C, "infer_mode",
        lambda *args, **kwargs: ModeDecision(
            mode=Mode.T2VA, confidence=1.0, rule_fired="test-no-assets"
        ),
    )

    with pytest.raises(RuntimeError, match="captured before model invocation"):
        C.compile_brief(
            Brief(intent="A bird takes off", seconds=8.0),
            backend=DummyBackend(), opts=ProfileOptions(),
        )

    assert chosen == [(Mode.T2VA, "compose_base.v2.txt")]
