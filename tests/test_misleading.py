from __future__ import annotations

from immunocheck.application.abstention import SignalRecorder
from immunocheck.application.misleading import (
    FEW_SHOT_BLOCK,
    TECHNICAL_ABSTENTION,
    CombinedVerdictGenerator,
    PromptAugmentingClient,
    ResilientVerdictGenerator,
)
from immunocheck.application.text_components import ModelOutputError
from immunocheck.domain.models import DraftVerdict, Evidence, ExtractedClaim, Verdict

CLAIM = ExtractedClaim("Alegação.", 0.9)
EVIDENCE = (Evidence("d:p1:c1:a", "texto", "F", "D", "https://x"),)


class Fixed:
    def __init__(self, verdict: Verdict, sources=("d:p1:c1:a",)) -> None:
        self.verdict, self.sources, self.calls = verdict, sources, 0

    def generate(self, claim, evidence) -> DraftVerdict:
        self.calls += 1
        return DraftVerdict(self.verdict, f"via {self.verdict}", self.sources)


def test_relation_can_only_turn_a_conclusion_into_misleading() -> None:
    direct, relation = Fixed(Verdict.REFUTED), Fixed(Verdict.MISLEADING)
    assert CombinedVerdictGenerator(direct, relation).generate(CLAIM, EVIDENCE).verdict is (
        Verdict.MISLEADING
    )

    relation = Fixed(Verdict.SUPPORTED)
    result = CombinedVerdictGenerator(Fixed(Verdict.REFUTED), relation).generate(CLAIM, EVIDENCE)
    assert result.verdict is Verdict.REFUTED

    empty = Fixed(Verdict.MISLEADING, sources=())
    assert CombinedVerdictGenerator(Fixed(Verdict.SUPPORTED), empty).generate(
        CLAIM, EVIDENCE
    ).verdict is Verdict.SUPPORTED


def test_direct_abstention_is_never_reverted_and_skips_relation() -> None:
    relation = Fixed(Verdict.MISLEADING)
    result = CombinedVerdictGenerator(Fixed(Verdict.INSUFFICIENT_EVIDENCE), relation).generate(
        CLAIM, EVIDENCE
    )
    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE and relation.calls == 0


class Failing:
    def generate(self, claim, evidence):
        raise ModelOutputError("saída inválida")


def test_resilient_generator_turns_invalid_output_into_flagged_abstention() -> None:
    recorder = SignalRecorder()
    recorder.reset()
    draft = ResilientVerdictGenerator(Failing(), recorder).generate(CLAIM, EVIDENCE)
    assert draft.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert draft.explanation == TECHNICAL_ABSTENTION and draft.source_ids == ()
    assert recorder._state.technical_abstention is True


def test_prompt_augmenting_client_appends_extra_text_only_to_system_prompt() -> None:
    seen = {}

    class Client:
        def chat(self, **kwargs):
            seen.update(kwargs)
            return {}

    PromptAugmentingClient(Client(), FEW_SHOT_BLOCK).chat(
        system_prompt="base", user_prompt="u", schema={}, max_output_tokens=5
    )
    assert seen["system_prompt"].startswith("base") and "tétano" in seen["system_prompt"]
    assert seen["user_prompt"] == "u"
    assert "PARTIAL_WITH_DISTORTION" in FEW_SHOT_BLOCK
