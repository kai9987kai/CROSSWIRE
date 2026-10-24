"""Closed-loop dynamic runtime shield for black-box deployment.

In open-loop deployment, an admitted word is dispatched unconditionally. Under
latent drift, unmodeled delays, or assumption violations, intermediate outputs
may contradict the surviving models or reveal that subsequent actions lead to an
absorbing hazard. The dynamic runtime shield monitors intermediate outputs at
every step, updates the active survivor set, and halts or re-plans before
hazardous actions are executed.
"""
from __future__ import annotations

from itertools import product
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
                 contract: Contract, mode: str = "shielded", cancel: Callable[[], bool] | None = None,
                 fault_schedule: dict | None = None):
        if mode not in ('open_loop', 'shielded', 'recovery', 'replan'):
            raise ValueError('Unknown execution mode')
        self.space = space
        self.contract = contract
        self.mode = mode
        self.cancel = cancel
        self.fault_schedule = fault_schedule
        self.change_point_step = fault_schedule.get('step') if fault_schedule else None
        self.fault_type = fault_schedule.get('type') if fault_schedule else None
        self.change_point_detected = False
        self.detection_step = None
        self.detection_latency = None
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
        self.replanned = False
        self.replan_events: list[dict] = []
        self.replanned_suffix: tuple[int, ...] | None = None

    def _check_change_point_detection(self, current_step_index: int):
        if self.fault_schedule and self.change_point_step is not None:
            if current_step_index >= self.change_point_step and not self.change_point_detected:
                self.change_point_detected = True
                self.detection_step = current_step_index
                self.detection_latency = current_step_index - self.change_point_step

    def change_point_record(self) -> dict:
        return {
            'scheduled': self.fault_schedule is not None,
            'step': self.change_point_step,
            'type': self.fault_type,
            'detected': self.change_point_detected,
            'detection_step': self.detection_step,
            'detection_latency': self.detection_latency,
        }

    def _find_safe_suffix(self, prefix: tuple[int, ...], remaining_horizon: int) -> tuple[int, ...] | None:
        """Find shortest lexicographic action suffix satisfying the contract under all active survivors."""
        if not self.active_survivors or remaining_horizon <= 0:
            return None
        for length in range(1, remaining_horizon + 1):
            for cand in product(range(self.space.machine.inputs), repeat=length):
                full = prefix + cand
                if all(self.contract.accepts(self.space.semantic(aid, full)) for aid in self.active_survivors):
                    return cand
        return None

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
            self._check_change_point_detection(len(self.history_words))
            self.status = "INTERVENED_ANOMALY"
            self.intervened = True
            self.reasons.append("Pre-step abort: no surviving models match history (anomaly/drift detected)")
            if self.mode in ("recovery", "replan"):
                rec_out = self.recover(target)
                return rec_out, False
            return None, False

        # Consensus safety requires every surviving interpretation to permit the
        # next action, including before the first target observation is available.
        candidate_prefix = tuple(self.history_words) + (planned_action,)
        if any(self.contract.hazard in self.space.semantic(aid, candidate_prefix)
               for aid in self.active_survivors):
            if self.mode == "replan":
                rem_h = max(0, self.contract.horizon - len(self.history_words))
                safe_suffix = self._find_safe_suffix(tuple(self.history_words), rem_h)
                if safe_suffix is not None:
                    self._check_change_point_detection(len(self.history_words))
                    self.replanned = True
                    self.replan_events.append({
                        'step': len(self.history_words), 'trigger': 'pre_step_hazard',
                        'old_action': planned_action, 'new_suffix': list(safe_suffix),
                        'survivor_count': len(self.active_survivors)
                    })
                    self.status = "REPLANNED_ONLINE_SAFE"
                    self.reasons.append(f"Replanned online at step {len(self.history_words)}: switched to safe suffix {list(safe_suffix)}")
                    planned_action = safe_suffix[0]
                    self.replanned_suffix = safe_suffix[1:]
                else:
                    self._check_change_point_detection(len(self.history_words))
                    self.status = "INTERVENED_HAZARD_AVERTED"
                    self.intervened = True
                    self.hazard_averted = True
                    self.reasons.append(f"Pre-step abort at step {len(self.history_words) + 1}: action {planned_action} risks hazard and no safe replan exists")
                    rec_out = self.recover(target)
                    return rec_out, False
            else:
                self._check_change_point_detection(len(self.history_words))
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
            self._check_change_point_detection(len(self.history_words) - 1)
            self.status = "INTERVENED_ANOMALY"
            self.intervened = True
            self.reasons.append(f"Post-step abort at step {len(self.history_words)}: output {out} refuted all surviving adapters")
            if self.mode in ("recovery", "replan"):
                self.recover(target)
                return out, False
            return out, False

        # If there are remaining planned steps, check if the remaining suffix is still safe
        rem_plan_to_check = self.replanned_suffix if self.replanned_suffix is not None else remaining_plan
        if rem_plan_to_check:
            full_plan = current_word + tuple(rem_plan_to_check)
            suffix_hazardous = any(
                self.contract.hazard in self.space.semantic(adapter_id, full_plan)
                for adapter_id in self.active_survivors
            )
            suffix_misses_goal = (self.mode == "replan") and any(
                not self.contract.accepts(self.space.semantic(adapter_id, full_plan))
                for adapter_id in self.active_survivors
            )

            if suffix_hazardous or suffix_misses_goal:
                if self.mode == "replan":
                    rem_h = max(0, self.contract.horizon - len(self.history_words))
                    safe_suffix = self._find_safe_suffix(current_word, rem_h)
                    if safe_suffix is not None:
                        self._check_change_point_detection(len(self.history_words) - 1)
                        self.replanned = True
                        self.replan_events.append({
                            'step': len(self.history_words), 'trigger': 'post_step_suffix_risk',
                            'old_suffix': list(rem_plan_to_check), 'new_suffix': list(safe_suffix),
                            'survivor_count': len(self.active_survivors)
                        })
                        self.status = "REPLANNED_ONLINE_SAFE"
                        self.reasons.append(f"Replanned online at step {len(self.history_words)}: switched to safe suffix {list(safe_suffix)}")
                        self.replanned_suffix = safe_suffix
                        return out, True
                    else:
                        self._check_change_point_detection(len(self.history_words) - 1)
                        self.status = "INTERVENED_HAZARD_AVERTED"
                        self.intervened = True
                        self.hazard_averted = True
                        self.reasons.append(f"Post-step abort at step {len(self.history_words)}: upcoming plan suffix risks hazard and no safe replan exists")
                        self.recover(target)
                        return out, False
                else:
                    self._check_change_point_detection(len(self.history_words) - 1)
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
                       mode: str = "open_loop", cancel: Callable[[], bool] | None = None,
                       fault_schedule: dict | None = None) -> dict:
    """Execute deployment through the target process with optional closed-loop shielding."""
    if hasattr(target, 'set_phase'):
        target.set_phase('deployment')
    shield = RuntimeShield(space, survivors, contract, mode=mode, cancel=cancel, fault_schedule=fault_schedule)
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
        plan = list(planned_word)
        step_idx = 0
        while step_idx < len(plan):
            _check_cancel(cancel)
            action = plan[step_idx]
            remaining = plan[step_idx + 1:]
            _, should_continue = shield.step(target, action, remaining)
            if shield.replanned_suffix is not None:
                plan = plan[:step_idx + 1] + list(shield.replanned_suffix)
                shield.replanned_suffix = None
            if not should_continue:
                break
            step_idx += 1

        deployment["complete"] = (len(shield.history_words) == len(plan)) and not shield.intervened
        deployment["shield_status"] = shield.status if shield.intervened else ("REPLANNED_ONLINE_SAFE" if shield.replanned else "COMPLETED")

    except InterfaceError as exc:
        deployment["error"] = {"code": exc.code, "message": str(exc)}
        deployment["shield_status"] = "INTERFACE_ERROR"
    finally:
        deployment["executed_word"] = list(shield.history_words)
        deployment["outputs"] = list(shield.history_outputs)
        deployment["intervened"] = shield.intervened
        deployment["hazard_averted"] = shield.hazard_averted
        deployment["replanned"] = shield.replanned
        deployment["replan_count"] = len(shield.replan_events)
        deployment["replan_events"] = list(shield.replan_events)
        deployment["reasons"] = list(shield.reasons)
        deployment["survivor_history"] = list(shield.survivor_counts)
        deployment["recovery"] = shield.recovery_record()
        deployment["change_point"] = shield.change_point_record()
        deployment["target_steps"] = target.counts["step_attempts"] - previous_counts["step_attempts"]
        deployment["resets"] = target.counts["reset_attempts"] - previous_counts["reset_attempts"]
        deployment["target_calls"] = target.counts["target_calls"] - previous_counts["target_calls"]

    return deployment


def synthesize_safe_return(space: CandidateSpace, survivors, prefix=(), max_length: int | None = None) -> dict:
    """Synthesize a certified hazard-free return-to-initial (soft reset) or stabilizing suffix.

    Searches for the shortest action suffix `w_ret` within the remaining horizon such that:
    1. `prefix + w_ret` is hazard-free under every surviving model in `survivors`.
    2. `prefix + w_ret` returns the reference state machine to `space.machine.initial` across
       every surviving model (certified soft return-to-home).
    If no return-to-initial path exists within the horizon, falls back to the shortest
    universally hazard-free holding step if one exists.
    """
    survivors = space._ids(survivors)
    prefix = tuple(prefix)
    if not survivors:
        return {
            'certified': False, 'return_to_initial': False, 'word': None,
            'reason': 'empty_belief', 'candidate_count': 0,
        }
    if prefix and not space.probe_is_safe(survivors, prefix):
        return {
            'certified': False, 'return_to_initial': False, 'word': None,
            'reason': 'prefix_already_hazardous', 'candidate_count': len(survivors),
        }

    def _end_state(input_map, full_word):
        state = space.machine.initial
        for sym in full_word:
            state, out = space.machine.transitions[state][input_map[sym]]
            if out == space.contract.hazard:
                return None
        return state

    if hasattr(space, 'decompose_id'):
        active_maps = [space.input_perms[i_idx] for i_idx in sorted({space.decompose_id(i)[0] for i in survivors})]
    else:
        seen_maps = []
        for i in survivors:
            im = space.adapters[i].input_map
            if im not in seen_maps:
                seen_maps.append(im)
        active_maps = seen_maps

    if all(_end_state(im, prefix) == space.machine.initial for im in active_maps):
        return {
            'certified': True, 'return_to_initial': True, 'word': [],
            'reason': 'already_at_initial', 'candidate_count': len(survivors),
        }

    rem = max(0, space.contract.horizon - len(prefix)) if max_length is None else max(0, int(max_length))
    if rem <= 0:
        return {
            'certified': False, 'return_to_initial': False, 'word': None,
            'reason': 'horizon_exhausted', 'candidate_count': len(survivors),
        }

    for length in range(1, rem + 1):
        for cand in product(range(space.machine.inputs), repeat=length):
            full = prefix + cand
            if all(_end_state(im, full) == space.machine.initial for im in active_maps):
                return {
                    'certified': True, 'return_to_initial': True, 'word': list(cand),
                    'reason': 'certified_return_to_initial', 'candidate_count': len(survivors),
                }

    for action in range(space.machine.inputs):
        full = prefix + (action,)
        if all(_end_state(im, full) is not None for im in active_maps):
            return {
                'certified': True, 'return_to_initial': False, 'word': [action],
                'reason': 'certified_safe_hold', 'candidate_count': len(survivors),
            }

    return {
        'certified': False, 'return_to_initial': False, 'word': None,
        'reason': 'no_safe_continuation', 'candidate_count': len(survivors),
    }
