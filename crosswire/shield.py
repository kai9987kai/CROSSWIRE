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


def _check_cancel(cancel):
    if cancel and cancel():
        from .study import Cancelled
        raise Cancelled('Deployment cancelled by user')


class RuntimeShield:
    """Monitors step-by-step target execution and intervenes when safety is violated."""

    def __init__(self, space: CandidateSpace, initial_survivors: tuple[int, ...],
                 contract: Contract, mode: str = "shielded", cancel: Callable[[], bool] | None = None):
        if mode not in ('open_loop', 'shielded', 'recovery'):
            raise ValueError('Unknown execution mode')
        self.space = space
        self.contract = contract
        self.mode = mode
        self.cancel = cancel
        self.active_survivors = space._ids(initial_survivors)
        self.history_words: list[int] = []
        self.history_outputs: list[int] = []
        self.survivor_counts: list[int] = [len(self.active_survivors)]
        self.status = "ACTIVE"
        self.intervened = False
        self.reasons: list[str] = []
        self.hazard_averted = False
        self.recovery_requested = False
        self.recovery_attempted = False
        self.recovery_certified = False
        self.recovery_succeeded = False
        self.recovery_reason = 'not_requested'
        self.recovery_action = None
        self.recovery_candidate_count = 0
        self.recovery_remaining_horizon = contract.horizon

    def _observe(self, action: int, output: int):
        self.history_words.append(action)
        self.history_outputs.append(output)
        word, outputs = tuple(self.history_words), tuple(self.history_outputs)
        self.active_survivors = tuple(aid for aid in self.active_survivors
                                      if self.space.predict(aid, word) == outputs)
        self.survivor_counts.append(len(self.active_survivors))

    def recovery_record(self) -> dict:
        return {'requested': self.recovery_requested, 'attempted': self.recovery_attempted,
                'certified': self.recovery_certified, 'succeeded': self.recovery_succeeded,
                'reason': self.recovery_reason, 'action': self.recovery_action,
                'candidate_count': self.recovery_candidate_count,
                'remaining_horizon': self.recovery_remaining_horizon,
                'scope': 'Conditional on target inclusion in the live finite model family, '
                         'stationarity, deterministic reset and truthful anchors. A consistent '
                         'response does not establish real-world safety or task completion.'}

    def recover(self, target: TargetProcess) -> int | None:
        """Execute one model-safe fallback only while the live belief remains valid.

        Refutation supplies no replacement safety model. Without an independently
        specified backup controller, the only justified response is to halt.
        """
        self.recovery_requested = True
        self.recovery_succeeded = False
        self.recovery_certified = False
        self.recovery_action = None
        prefix, outputs = tuple(self.history_words), tuple(self.history_outputs)
        self.active_survivors = tuple(aid for aid in self.active_survivors
                                      if self.space.predict(aid, prefix) == outputs)
        self.recovery_candidate_count = len(self.active_survivors)
        self.recovery_remaining_horizon = max(0, self.contract.horizon - len(prefix))
        if not self.active_survivors:
            self.recovery_reason = 'model_contradicted'
            self.reasons.append('Recovery withheld: no model remains consistent with observed history')
            return None
        if not self.recovery_remaining_horizon:
            self.recovery_reason = 'horizon_exhausted'
            self.reasons.append('Recovery withheld: contract horizon is exhausted')
            return None
        safe_action = next((action for action in range(self.space.machine.inputs)
                            if all(self.contract.hazard not in self.space.semantic(aid, prefix + (action,))
                                   for aid in self.active_survivors)), None)
        if safe_action is None:
            self.recovery_reason = 'no_safe_action'
            self.reasons.append('Recovery withheld: no action is hazard-free under every live model')
            return None
        self.recovery_action = safe_action
        self.recovery_certified = True
        _check_cancel(self.cancel)
        self.recovery_attempted = True
        try:
            out = target.step(safe_action)
        except InterfaceError:
            self.recovery_reason = 'interface_error'
            raise
        self._observe(safe_action, out)
        if not self.active_survivors:
            self.recovery_reason = 'response_contradiction'
            self.status = 'INTERVENED_ANOMALY'
            self.hazard_averted = False
            self.reasons.append('Recovery response contradicted every certifying model; safety is unresolved')
            return out
        self.recovery_succeeded = True
        self.recovery_reason = 'certified_response'
        self.status = 'RECOVERED_SAFE_FALLBACK'
        self.reasons.append('Model-certified fallback executed with a response consistent with the live belief')
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
                return rec_out, False
            return None, False

        # Execute single step
        out = target.step(planned_action)
        self._observe(planned_action, out)
        current_word = tuple(self.history_words)

        if not self.active_survivors:
            # Anomaly / distribution drift detected: target output contradicted all surviving models
            self.status = "INTERVENED_ANOMALY"
            self.intervened = True
            self.reasons.append(f"Post-step abort at step {len(self.history_words)}: output {out} refuted all surviving adapters")
            if self.mode == "recovery":
                self.recover(target)
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
                    return out, False
                return out, False

        return out, True


def execute_deployment(target: TargetProcess, planned_word: list[int], space: CandidateSpace,
                       survivors: tuple[int, ...], contract: Contract,
                       mode: str = "open_loop", cancel: Callable[[], bool] | None = None) -> dict:
    """Execute deployment through the target process with optional closed-loop shielding."""
    shield = RuntimeShield(space, survivors, contract, mode=mode, cancel=cancel)
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
        _check_cancel(cancel)
        target.reset()
        for i, action in enumerate(planned_word):
            _check_cancel(cancel)
            remaining = planned_word[i + 1:]
            _, should_continue = shield.step(target, action, remaining)
            if not should_continue:
                break

        deployment["complete"] = (len(shield.history_words) == len(planned_word)) and not shield.intervened
        deployment["shield_status"] = shield.status if shield.intervened else "COMPLETED"

    except InterfaceError as exc:
        deployment["error"] = {"code": exc.code, "message": str(exc)}
        deployment["shield_status"] = "INTERFACE_ERROR"
    finally:
        deployment["executed_word"] = list(shield.history_words)
        deployment["outputs"] = list(shield.history_outputs)
        deployment["intervened"] = shield.intervened
        deployment["hazard_averted"] = shield.hazard_averted
        deployment["reasons"] = list(shield.reasons)
        deployment["survivor_history"] = list(shield.survivor_counts)
        deployment["recovery"] = shield.recovery_record()
        deployment["target_steps"] = target.counts["step_attempts"] - previous_counts["step_attempts"]
        deployment["resets"] = target.counts["reset_attempts"] - previous_counts["reset_attempts"]
        deployment["target_calls"] = target.counts["target_calls"] - previous_counts["target_calls"]

    return deployment
