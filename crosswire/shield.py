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
        if mode not in ('open_loop', 'shielded', 'recovery'):
            raise ValueError('Unknown execution mode')
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
        self.recovery_attempted = False
        self.recovery_succeeded = False

    def recover(self, target: TargetProcess) -> int | None:
        """Simplex fallback: execute a certified minimum-hazard recovery action."""
        self.recovery_attempted = True
        eval_set = self.active_survivors if self.active_survivors else tuple(a.id for a in self.space.adapters)
        candidate_actions = list(range(self.space.machine.inputs))

        def hazard_count(a):
            prefix = tuple(self.history_words) + (a,)
            return sum(self.contract.hazard in self.space.semantic(aid, prefix) for aid in eval_set)

        safe_action = min(candidate_actions, key=lambda a: (hazard_count(a), a))
        out = target.step(safe_action)
        self.history_words.append(safe_action)
        self.history_outputs.append(out)
        self.recovery_succeeded = True
        return out

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

        # Pre-condition check: if survivors are already empty
        if not self.active_survivors:
            self.status = "INTERVENED_ANOMALY"
            self.intervened = True
            self.reasons.append("Pre-step abort: no surviving models match history (anomaly/drift detected)")
            if self.mode == "recovery":
                rec_out = self.recover(target)
                self.status = "RECOVERED_SAFE_FALLBACK"
                self.reasons.append("Simplex fail-safe recovery action executed")
                return rec_out, False
            return None, False

        # Consensus safety requires every surviving interpretation to permit the
        # next action, including before the first target observation is available.
        candidate_prefix = tuple(self.history_words) + (planned_action,)
        if any(self.contract.hazard in self.space.semantic(aid, candidate_prefix)
               for aid in self.active_survivors):
            self.status = "INTERVENED_HAZARD_AVERTED"
            self.intervened = True
            self.hazard_averted = True
            self.reasons.append(f"Pre-step abort at step {len(self.history_words) + 1}: action {planned_action} risks hazard under a surviving adapter")
            if self.mode == "recovery":
                rec_out = self.recover(target)
                self.status = "RECOVERED_SAFE_FALLBACK"
                self.reasons.append("Simplex fail-safe recovery action executed")
                return rec_out, False
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
            self.reasons.append(f"Post-step abort at step {len(self.history_words)}: output {out} refuted all surviving adapters")
            if self.mode == "recovery":
                self.recover(target)
                self.status = "RECOVERED_SAFE_FALLBACK"
                self.reasons.append("Simplex fail-safe recovery action executed")
                return out, False
            return out, False

        # If there are remaining planned steps, check if the remaining suffix is still safe
        if remaining_plan:
            full_plan = current_word + tuple(remaining_plan)
            # Check if ANY surviving adapter predicts a hazard on this suffix
            suffix_hazardous = any(
                self.contract.hazard in self.space.semantic(adapter_id, full_plan)
                for adapter_id in self.active_survivors
            )

            if suffix_hazardous:
                # The remaining planned steps are no longer unanimously safe
                self.status = "INTERVENED_HAZARD_AVERTED"
                self.intervened = True
                self.hazard_averted = True
                self.reasons.append(f"Post-step abort at step {len(self.history_words)}: upcoming plan suffix {remaining_plan} risks hazard under updated survivors")
                if self.mode == "recovery":
                    self.recover(target)
                    self.status = "RECOVERED_SAFE_FALLBACK"
                    self.reasons.append("Simplex fail-safe recovery action executed")
                    return out, False
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

        deployment["executed_word"] = list(shield.history_words)
        deployment["outputs"] = list(shield.history_outputs)
        deployment["complete"] = (len(deployment["executed_word"]) == len(planned_word)) and not shield.intervened
        deployment["shield_status"] = shield.status if shield.intervened else "COMPLETED"
        deployment["intervened"] = shield.intervened
        deployment["hazard_averted"] = shield.hazard_averted
        deployment["reasons"] = shield.reasons
        deployment["survivor_history"] = shield.survivor_counts
        deployment["recovery"] = {
            "attempted": shield.recovery_attempted,
            "succeeded": shield.recovery_succeeded,
        }

    except InterfaceError as exc:
        deployment["executed_word"] = list(shield.history_words)
        deployment["outputs"] = getattr(exc, "trace", {}).get("outputs", list(shield.history_outputs))
        deployment["error"] = {"code": exc.code, "message": str(exc)}
        deployment["shield_status"] = "INTERFACE_ERROR"
    finally:
        deployment["target_steps"] = target.counts["step_attempts"] - previous_counts["step_attempts"]
        deployment["resets"] = target.counts["reset_attempts"] - previous_counts["reset_attempts"]
        deployment["target_calls"] = target.counts["target_calls"] - previous_counts["target_calls"]

    return deployment
