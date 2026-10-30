"""Canonical experimental conditions shared by study analyses and reports."""
from __future__ import annotations

import json

from .identity import canonical_json


CONDITION_DEFAULTS = {
    'anchors': False, 'split': 'development', 'horizon': 4,
    'execution_mode': 'open_loop', 'temporal': False, 'escalate': False,
    'probe_safety': 'unrestricted', 'risk_tolerance': 0.0, 'fault_schedule': None,
}
FAULT_TYPES = ('sensor_drift', 'actuator_swap', 'delay_spike', 'stuck_output', 'semantic_swap')
FAULT_PHASES = ('calibration', 'deployment', 'always')


def normalize_fault_schedule(value):
    """Validate and copy a schedule; omitted defaults identify the same condition."""
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError('fault_schedule must be a dict or None')
    if not {'step', 'type'} <= set(value):
        raise ValueError("fault_schedule must specify 'step' and 'type'")
    if set(value) - {'step', 'type', 'phase', 'value'}:
        raise ValueError('Unknown fault_schedule fields')
    if type(value['step']) is not int or value['step'] < 0:
        raise ValueError("fault_schedule 'step' must be a non-negative integer")
    if value['type'] not in FAULT_TYPES:
        raise ValueError(f"fault_schedule 'type' must be one of {FAULT_TYPES}")
    phase = value.get('phase', 'deployment')
    if phase not in FAULT_PHASES:
        raise ValueError(f"fault_schedule 'phase' must be one of {FAULT_PHASES}")
    result = {'step': value['step'], 'type': value['type'], 'phase': phase}
    if value['type'] == 'stuck_output':
        symbol = value.get('value', 0)
        if type(symbol) is not int or not 0 <= symbol < 4:
            raise ValueError("fault_schedule 'value' must be an integer in [0, 3]")
        result['value'] = symbol
    elif 'value' in value:
        raise ValueError("fault_schedule 'value' applies only to stuck_output")
    return result


def condition_key(configuration: dict) -> tuple:
    """Hashable, sortable identity, including canonical nested fault settings."""
    return tuple(canonical_json(normalize_fault_schedule(configuration.get(key)))
                 if key == 'fault_schedule' else configuration.get(key, default)
                 for key, default in CONDITION_DEFAULTS.items())


def condition_fields(key: tuple) -> dict:
    result = dict(zip(CONDITION_DEFAULTS, key))
    result['fault_schedule'] = json.loads(result['fault_schedule'])
    return result
