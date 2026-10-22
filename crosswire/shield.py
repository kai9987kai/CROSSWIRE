"""Closed-loop dynamic runtime shield for black-box deployment.

In open-loop deployment, an admitted word is dispatched unconditionally. Under
latent drift, unmodeled delays, or assumption violations, intermediate outputs
may contradict the surviving models or reveal that subsequent actions lead to an
absorbing hazard. The dynamic runtime shield monitors intermediate outputs at
every step, updates the active survivor set, and halts or re-plans before
hazardous actions are executed.
"""
from __future__ import annotations

from typing import Callable
from .core import CandidateSpace, Contract
from .interfaces import InterfaceError, TargetProcess


class RuntimeShield:
    """Monitors step-by-step target execution and intervenes when safety is violated."""

    def __init__(self, space: CandidateSpace, initial_survivors: tuple[int, ...],
                 contract: Contract, mode: str = "shielded"):
        self.space = space
        self.contract = contract
        self.mode = mode
        self.active_survivors = tuple(initial_survivors)
        self.history_words: list[int] = []
        self.history_outputs: list[int] = []
        self.survivor_counts: list[int] = [len(self.active_survivors)]
        self.status = "ACTIVE"
        self.intervened = False
        self.reasons: list[str] = []
        self.hazard_averted = False

    def step(self, target: TargetProcess, planned_action: int, remaining_plan: list[int]) -> tuple[int | None, bool]:
        """Execute one step with active pre- and post-condition safety guards.

        Returns (output, should_continue).
        """
        if self.mode == "open_loop":
            # Unshielded: directly step the target
            out = target.step(planned_action)
            self.history_words.append(planned_action)
            self.history_outputs.append(out)
            return out, True

        # Pre-condition check: if survivors are already empty or if action is universally hazardous
        if not self.active_survivors:
            self.status = "INTERVENED_ANOMALY"
            self.intervened = True
            self.hazard_averted = True
            self.reasons.append("Pre-step abort: no surviving models match history (anomaly/drift detected)")
            return None, False

        # Execute single step
        out = target.step(planned_action)
        self.history_words.append(planned_action)
        self.history_outputs.append(out)

        # Post-condition check: filter surviving adapters against the observed output
        current_word = tuple(self.history_words)
        current_outputs = tuple(self.history_outputs)
        next_survivors = []
        for adapter_id in self.active_survivors:
            pred = self.space.predict(adapter_id, current_word)
            if pred == current_outputs:
                next_survivors.append(adapter_id)
        self.active_survivors = tuple(next_survivors)
        self.survivor_counts.append(len(self.active_survivors))

        if not self.active_survivors:
            # Anomaly / distribution drift detected: target output contradicted all surviving models
            self.status = "INTERVENED_ANOMALY"
            self.intervened = True
            self.hazard_averted = True
            self.reasons.append(f"Post-step abort at step {len(self.history_words)}: output {out} refuted all surviving adapters")
            return out, False

        # If there are remaining planned steps, check if the remaining suffix is still safe
        if remaining_plan:
            full_plan = current_word + tuple(remaining_plan)
            # Check if ANY surviving adapter predicts a hazard on this suffix
            suffix_hazardous = False
            for adapter_id in self.active_survivors:
                semantic_trace = self.space.semantic(adapter_id, full_plan)
                if self.contract.hazard in semantic_trace:
                    suffix_hazardous = True
                    break

            if suffix_hazardous:
                # The remaining planned steps are no longer unanimously safe
                self.status = "INTERVENED_HAZARD_AVERTED"
                self.intervened = True
                self.hazard_averted = True
                self.reasons.append(f"Post-step abort at step {len(self.history_words)}: upcoming plan suffix {remaining_plan} risks hazard under updated survivors")
                return out, False

        return out, True


def execute_deployment(target: TargetProcess, planned_word: list[int], space: CandidateSpace,
                       survivors: tuple[int, ...], contract: Contract,
                       mode: str = "open_loop", cancel: Callable[[], bool] | None = None) -> dict:
    """Execute deployment through the target process with optional closed-loop shielding."""
    shield = RuntimeShield(space, survivors, contract, mode=mode)
    deployment = {
        "word": list(planned_word),
        "executed_word": [],
        "outputs": [],
        "complete": False,
        "mode": mode,
        "shield_status": "COMPLETED" if mode == "open_loop" else "ACTIVE",
        "intervened": False,
        "hazard_averted": False,
        "reasons": [],
        "survivor_history": [len(survivors)],
        "target_steps": 0,
        "resets": 0,
        "target_calls": 0,
        "error": None,
    }

    previous_counts = dict(target.counts)
    try:
        target.reset()
        for i, action in enumerate(planned_word):
            if cancel and cancel():
                raise InterfaceError("cancelled", "Deployment cancelled by user")
            remaining = planned_word[i + 1:]
            out, should_continue = shield.step(target, action, remaining)
            if out is not None:
                deployment["executed_word"].append(action)
                deployment["outputs"].append(out)
            if not should_continue:
                break

        deployment["complete"] = (len(deployment["executed_word"]) == len(planned_word)) and not shield.intervened
        deployment["shield_status"] = shield.status if shield.intervened else "COMPLETED"
        deployment["intervened"] = shield.intervened
        deployment["hazard_averted"] = shield.hazard_averted
        deployment["reasons"] = shield.reasons
        deployment["survivor_history"] = shield.survivor_counts

    except InterfaceError as exc:
        deployment["outputs"] = getattr(exc, "trace", {}).get("outputs", deployment["outputs"])
        deployment["error"] = {"code": exc.code, "message": str(exc)}
        deployment["shield_status"] = "INTERFACE_ERROR"
    finally:
        deployment["target_steps"] = target.counts["step_attempts"] - previous_counts["step_attempts"]
        deployment["resets"] = target.counts["reset_attempts"] - previous_counts["reset_attempts"]
        deployment["target_calls"] = target.counts["target_calls"] - previous_counts["target_calls"]

    return deployment
