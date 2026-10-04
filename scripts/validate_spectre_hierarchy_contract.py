#!/usr/bin/env python3
"""Validate scalarized producer/consumer contracts in a Spectre netlist."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RANGE_RE = re.compile(r"^(.*)<(-?\d+):(-?\d+)>$")
NETLIST_RANGE_RE = re.compile(r"<-?\d+:-?\d+>")


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Instance:
    name: str
    master: str
    nets: tuple[str, ...]


@dataclass
class Subckt:
    ports: tuple[str, ...]
    instances: dict[str, Instance]


def normalize_name(value: str) -> str:
    return value.replace(r"\<", "<").replace(r"\>", ">")


def logical_lines(text: str) -> list[str]:
    result: list[str] = []
    current = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("*"):
            continue
        continued = line.endswith("\\")
        if continued:
            line = line[:-1].rstrip()
        current = f"{current} {line}".strip()
        if not continued:
            result.append(normalize_name(current))
            current = ""
    if current:
        raise ContractError("unterminated Spectre continuation")
    return result


def parse_netlist(path: Path) -> dict[str, Subckt]:
    subckts: dict[str, Subckt] = {}
    active_name: str | None = None
    active: Subckt | None = None
    for line in logical_lines(path.read_text(encoding="utf-8")):
        if line.startswith("subckt "):
            tokens = line.split()
            if len(tokens) < 2 or active is not None:
                raise ContractError(f"invalid nested subckt statement: {line}")
            active_name = tokens[1]
            if active_name in subckts:
                raise ContractError(f"duplicate subckt {active_name}")
            active = Subckt(tuple(tokens[2:]), {})
            subckts[active_name] = active
            continue
        if line.startswith("ends "):
            if active is None or line.split()[1] != active_name:
                raise ContractError(f"mismatched ends statement: {line}")
            active_name = None
            active = None
            continue
        if active is None:
            continue
        match = re.match(r"^(\S+)\s+\(([^)]*)\)\s+(\S+)(?:\s+.*)?$", line)
        if not match:
            continue
        name, nets_text, master = match.groups()
        if name in active.instances:
            raise ContractError(f"duplicate instance {active_name}.{name}")
        active.instances[name] = Instance(name, master, tuple(nets_text.split()))
    if active is not None:
        raise ContractError(f"unterminated subckt {active_name}")
    return subckts


def expand_ports(expression: str) -> list[str]:
    expression = normalize_name(expression)
    match = RANGE_RE.match(expression)
    if not match:
        return [expression]
    stem, start_text, stop_text = match.groups()
    start, stop = int(start_text), int(stop_text)
    step = 1 if stop >= start else -1
    return [f"{stem}<{index}>" for index in range(start, stop + step, step)]


def endpoint_ports(spec: dict[str, Any]) -> list[str]:
    ports = spec.get("ports")
    if isinstance(ports, str):
        return expand_ports(ports)
    if isinstance(ports, list) and ports and all(isinstance(item, str) for item in ports):
        result: list[str] = []
        for item in ports:
            result.extend(expand_ports(item))
        return result
    raise ContractError(f"invalid endpoint ports: {ports!r}")


def endpoint_key(instance: str, port: str) -> str:
    return f"{instance}.{port}"


def resolve_endpoint(
    subckts: dict[str, Subckt], parent: Subckt, instance_name: str, port: str
) -> str:
    instance = parent.instances.get(instance_name)
    if instance is None:
        raise ContractError(f"missing parent instance {instance_name}")
    master = subckts.get(instance.master)
    if master is None:
        raise ContractError(f"missing master subckt {instance.master} for {instance_name}")
    if len(instance.nets) != len(master.ports):
        raise ContractError(
            f"port-count mismatch {instance_name}/{instance.master}: "
            f"instance={len(instance.nets)} master={len(master.ports)}"
        )
    matches = [index for index, name in enumerate(master.ports) if name == port]
    if len(matches) != 1:
        raise ContractError(
            f"expected one master port {instance_name}.{port}, found {len(matches)}"
        )
    return instance.nets[matches[0]]


def validate(subckts: dict[str, Subckt], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    parent_name = contract.get("parent_subckt")
    parent = subckts.get(parent_name)
    if parent is None:
        raise ContractError(f"missing parent subckt {parent_name!r}")
    # Range notation is supported in contract ports, not in netlist topology.
    # Treating an array as one literal endpoint would undercount its fanout.
    for instance in parent.instances.values():
        master = subckts.get(instance.master)
        tokens = (instance.name, *instance.nets, *(master.ports if master else ()))
        if any(NETLIST_RANGE_RE.search(token) for token in tokens):
            raise ContractError(
                f"unexpanded netlist range at {parent_name}.{instance.name}; "
                "provide scalarized instances, master ports, and nets with explicit "
                "broadcast or bitwise mapping"
            )
    patterns = [re.compile(item) for item in contract.get("automatic_net_patterns", [])]
    waivers: set[str] = set()
    for waiver in contract.get("waivers", []):
        reason = waiver.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ContractError(f"waiver lacks a reason: {waiver!r}")
        for port in endpoint_ports(waiver):
            waivers.add(endpoint_key(waiver["instance"], port))

    all_endpoints: dict[str, set[str]] = {}
    for instance in parent.instances.values():
        master = subckts.get(instance.master)
        if master is None or len(master.ports) != len(instance.nets):
            continue
        for port, net in zip(master.ports, instance.nets):
            all_endpoints.setdefault(net, set()).add(endpoint_key(instance.name, port))

    producer_nets: dict[str, list[str]] = {}
    required_endpoints: set[str] = set()
    for relation in contract.get("connections", []):
        relation_id = relation.get("id", "unnamed")
        producer = relation.get("producer")
        consumers = relation.get("consumers")
        if not isinstance(producer, dict) or not isinstance(consumers, list) or not consumers:
            raise ContractError(f"connection {relation_id} needs one producer and consumers")
        producer_ports = endpoint_ports(producer)
        consumer_ports = [endpoint_ports(item) for item in consumers]
        if any(len(ports) != len(producer_ports) for ports in consumer_ports):
            raise ContractError(f"connection {relation_id} has unequal bus widths")
        for bit_index, producer_port in enumerate(producer_ports):
            producer_key = endpoint_key(producer["instance"], producer_port)
            required_endpoints.add(producer_key)
            producer_net = resolve_endpoint(
                subckts, parent, producer["instance"], producer_port
            )
            producer_nets.setdefault(producer_net, []).append(producer_key)
            expected = {producer_key}
            for consumer, ports in zip(consumers, consumer_ports):
                consumer_port = ports[bit_index]
                consumer_key = endpoint_key(consumer["instance"], consumer_port)
                required_endpoints.add(consumer_key)
                expected.add(consumer_key)
                consumer_net = resolve_endpoint(
                    subckts, parent, consumer["instance"], consumer_port
                )
                if consumer_net != producer_net:
                    errors.append(
                        f"{relation_id}[{bit_index}] disconnected: {producer_key}={producer_net} "
                        f"but {consumer_key}={consumer_net}"
                    )
            actual = all_endpoints.get(producer_net, set()) - waivers
            if actual != expected:
                errors.append(
                    f"{relation_id}[{bit_index}] fanout mismatch on {producer_net}: "
                    f"expected={sorted(expected)} actual={sorted(actual)}"
                )
            if any(pattern.search(producer_net) for pattern in patterns):
                errors.append(
                    f"{relation_id}[{bit_index}] required connection uses automatic net {producer_net}"
                )

    for net, producers in producer_nets.items():
        if len(producers) != 1:
            errors.append(f"multiple required producers on {net}: {sorted(producers)}")

    for net, endpoints in all_endpoints.items():
        active = endpoints - waivers
        if len(active) == 1 and any(pattern.search(net) for pattern in patterns):
            endpoint = next(iter(active))
            if endpoint in required_endpoints:
                errors.append(f"single-ended required endpoint {endpoint} on {net}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--netlist", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        errors = validate(parse_netlist(args.netlist), contract)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
