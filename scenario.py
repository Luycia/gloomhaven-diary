from __future__ import annotations

import graphviz
import json
import warnings
import os

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from enum import Enum
from typing import List, Dict, Set


class ScenarioNotFoundException(Exception):
    """Exception raised if a given scenario is not found. For example if it's not unlocked yet or not saved."""

    def __init__(self, scenario_id) -> None:
        super().__init__(f"Scenario ID {scenario_id} not found")


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class AchievementType(Enum):
    GROUP = 0
    GLOBAL = 1


class AchievementStatus(Enum):
    OPEN = 0
    CLOSED = 1


@dataclass
class Achievement:
    name: str
    type: AchievementType
    status: AchievementStatus

    def __str__(self) -> str:
        return f"{self.name} ({self.type.name}) {self.status.name}"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return super.__hash__((self.name, self.type.name, self.status.name))


@dataclass_json
@dataclass
class Scenario:
    id: str
    name: str = None
    aim: str = None
    successors: Set[str] = field(default_factory=list)
    predecessors: Set[str] = field(default_factory=list)
    difficulty: Difficulty = None
    attempts: int = None
    description: str = None
    rewards: List[str] = field(default_factory=list)
    achievements: List[Achievement] = field(default_factory=list)
    requirements: List[Achievement] = field(default_factory=list)
    played: bool = False

    def formatted(self):
        return f"Nr. {self.id} {self.name}\nVoraussetzungen: {self.requirements}\nZiel: {self.aim}\nVorgänger: {self.predecessors}\nNachfolger: {self.successors}\nSchwierigkeit: {self.difficulty.name if self.difficulty else None}, Versuche: {self.attempts}\nBelohnungen: {self.rewards}\nNeue Orte: {self.successors}\n{self.description}"

    def short_formatted(self):
        return f"Nr. {self.id} {self.name if self.name else ''}"


class ScenarioManager:
    def __init__(self, scenarios: Dict[str, Scenario]) -> None:
        self.scenarios = scenarios
        self.__link_scenarios()

    def __link_scenarios(self):
        new_scenarios = []
        for scenario in self.scenarios.values():
            for successor_id in scenario.successors:
                if not successor_id.isnumeric():
                    continue
                if successor_id in self.scenarios:
                    # Link successor scenario with predecessor
                    successor = self.scenarios[successor_id]
                    successor.predecessors.add(scenario.id)
                else:
                    # Successor scenario not exists yet and thus will be created
                    new_scenarios.append(
                        Scenario(id=successor_id, predecessors={scenario.id})
                    )

        for scenario in new_scenarios:
            self.scenarios[scenario.id] = scenario

    def render_tree(self, output_path: str, format: str = "pdf"):
        tree = graphviz.Digraph(
            "scenario-tree",
            filename=output_path,
            node_attr={"color": "lightblue2", "style": "filled"},
            format=format,
        )

        tree.attr(size="7,5")
        for scenario in self.scenarios.values():
            if format != "svg":
                tree.node(name=scenario.id, label=scenario.formatted())
            else:
                tree.node(
                    name=scenario.id,
                    label=scenario.short_formatted(),
                    tooltip=scenario.formatted(),
                )

            if not scenario.played:
                # color node for better visuals
                node_repr = tree.body[-1]
                node_repr = node_repr[:-2] + " color=lemonchiffon2" + node_repr[-2:]
                tree.body[-1] = node_repr

            for successor in scenario.successors:
                if successor.isnumeric():
                    tree.edge(scenario.id, successor)

        tree.view()

    def render_scenario_tree(
        self, output_path: str, scenario_id: str, format: str = "pdf", max_hop=None
    ):
        if scenario_id not in self.scenarios:
            raise ScenarioNotFoundException(scenario_id)

        output_path = "{}-{}{}".format(
            os.path.splitext(output_path)[0],
            scenario_id,
            os.path.splitext(output_path)[1],
        )

        tree = graphviz.Digraph(
            "scenario-tree",
            filename=output_path,
            node_attr={"color": "lightblue2", "style": "filled"},
            format=format,
        )
        tree.attr(size="7,5")
        tree.edge_attr.update(fontsize="11")

        work = [(self.scenarios[scenario_id], 0)]
        edges = {}

        for scenario, hop in work:
            if max_hop and hop > max_hop:
                continue
            if format != "svg":
                tree.node(name=scenario.id, label=scenario.formatted())
            else:
                tree.node(
                    name=scenario.id,
                    label=scenario.short_formatted(),
                    tooltip=scenario.formatted(),
                )

            for requirement in scenario.requirements:
                if requirement.status != AchievementStatus.CLOSED:
                    continue
                for pre in self.scenarios.values():
                    if any(w[0].id == pre.id for w in work):
                        continue
                    if requirement in pre.achievements:
                        work.append((pre, hop + 1))
                        edges[(pre.id, scenario.id)] = str(requirement)

            for predecessor_id in scenario.predecessors:
                if predecessor_id not in self.scenarios:
                    raise ScenarioNotFoundException(predecessor_id)

                predecessor = self.scenarios[predecessor_id]
                if (predecessor.id, scenario.id) not in edges:
                    edges[(predecessor.id, scenario.id)] = None

                if all(w[0].id != predecessor_id for w in work):
                    work.append((predecessor, hop + 1))

        for (e_from, e_to), label in edges.items():
            tree.edge(e_from, e_to, label=label)

        tree.view()

    def __str__(self) -> str:
        return "\n".join(
            [
                str(scenario)
                for scenario in sorted(self.scenarios.values(), key=lambda x: x.id)
            ]
        )

    def __repr__(self) -> str:
        return str([id for id in sorted(self.scenarios.values())])

    def __getitem__(self, item):
        return self.scenarios[item]

    def __setitem__(self, key, value):
        self.scenarios[key] = value

    def __len__(self) -> int:
        return len(self.scenarios)

    def keys(self):
        return sorted(self.scenarios.keys(), key=lambda x: int(x))

    def values(self):
        return sorted(self.scenarios.values(), key=lambda x: int(x.id))

    def short(self):
        return [scenario.short_formatted() for scenario in self.values()]

    def items(self):
        return self.scenarios.items()

    def to_json(self):
        return [json.loads(scenario.to_json()) for scenario in self.scenarios.values()]

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_json(), f, indent=4, sort_keys=True)

    @staticmethod
    def from_file(path: str) -> ScenarioManager:
        warnings.filterwarnings("ignore")
        with open(path) as f:
            scenarios = {
                scenario["id"]: Scenario.from_json(json.dumps(scenario))
                for scenario in json.load(f)
            }
        return ScenarioManager(scenarios)
