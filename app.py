import config
import PySimpleGUI as sg
from tkinter import messagebox
from typing import List, Dict

from scenario import (
    Achievement,
    Scenario,
    ScenarioManager,
    ScenarioNotFoundException,
    Difficulty,
    AchievementStatus,
    AchievementType,
)

APP_NAME = "Gloomhaven - Diary"
ROW_WIDTH = 65
FONT_SIZE = {"default": 13, "h1": 28, "h2": 22}
MAX_ACHIEVEMENTS = 5


def achievement_layout(i):
    return [
        sg.In(s=int(ROW_WIDTH * 0.5), key=("-SCENARIO_ACHIEVEMENT_NAME-", i)),
        sg.OptionMenu(
            values=[a.name for a in AchievementType],
            key=("-SCENARIO_ACHIEVEMENT_TYPE-", i),
            default_value=AchievementType.GROUP.name,
        ),
        sg.OptionMenu(
            values=[a.name for a in AchievementStatus],
            key=("-SCENARIO_ACHIEVEMENT_STATUS-", i),
            default_value=AchievementStatus.CLOSED.name,
        ),
        sg.Radio(
            "E",
            group_id=("SCENARIO_ACHIEVEMENT_CHECK", i),
            default=True,
            key=("-SCENARIO_ACHIEVEMENT_CHECK_A-", i),
        ),
        sg.Radio(
            "V",
            group_id=("SCENARIO_ACHIEVEMENT_CHECK", i),
            default=False,
            key=("-SCENARIO_ACHIEVEMENT_CHECK_R-", i),
        ),
        sg.Button(
            image_filename="./assets/images/trash.png",
            key=("-SCENARIO_ACHIEVEMENT_DEL-", i),
        ),
    ]


def init_window(manager: ScenarioManager) -> sg.Window:
    sg.theme("LightBlue")
    TEXT_LEN = 14
    IN_LEN = ROW_WIDTH - TEXT_LEN

    achievements = sorted(manager.achievements, key=lambda x: x.name)

    general_layout = [
        [
            sg.Text("Szenario auswählen"),
            sg.OptionMenu(
                values=manager.short(),
                default_value=manager.short()[0],
                key="-VISUALIZE_SELECTOR-",
            ),
            sg.Button("Visualisieren", key="-VISUALIZE_RENDER-"),
        ],
        [
            sg.Button("Alle Visualisieren", key="-VISUALIZE_RENDER_ALL-"),
            sg.Button("Speichern", key="-GENERAL_SAVE-", s=10),
        ],
        [
            sg.Text("Entdeckte Orte:", key="-PBAR_LOCATIONS_COUNT-", size=14),
            sg.Text("%", key="-PBAR_LOCATIONS_PERCENTAGE-", s=11),
            sg.ProgressBar(
                config.COUNT_SCENARIOS, s=(ROW_WIDTH // 2, 12), key="-PBAR_LOCATIONS-"
            ),
        ],
        [
            sg.Text(f"Gespielte Szenarien:", key="-PBAR_PLAYED_COUNT-", size=14),
            sg.Text("%", key="-PBAR_PLAYED_PERCENTAGE-", s=11),
            sg.ProgressBar(
                config.COUNT_SCENARIOS, s=(ROW_WIDTH // 2, 12), key="-PBAR_PLAYED-"
            ),
        ],
        [sg.Text("Welt - Status")],
        [
            sg.Listbox(
                achievements,
                no_scrollbar=True,
                key="-GENERAL_WORLD_STATUS-",
                s=(IN_LEN, min(len(achievements), 20)),
                select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                default_values=manager.world_status,
            ),
        ],
        [
            sg.In(s=int(ROW_WIDTH * 0.45), key="-GENERAL_WORLD_STATUS_NAME-"),
            sg.OptionMenu(
                values=[a.name for a in AchievementType],
                key="-GENERAL_WORLD_STATUS_TYPE-",
                default_value=AchievementType.GROUP.name,
            ),
            sg.OptionMenu(
                values=[a.name for a in AchievementStatus],
                key="-GENERAL_WORLD_STATUS_STATUS-",
                default_value=AchievementStatus.CLOSED.name,
            ),
        ],
    ]

    achievements_layout = [
        sg.Column(
            [achievement_layout(i)],
            p=0,
            visible=False,
            key=("-SCENARIO_ACHIEVEMENT-", i),
        )
        for i in range(MAX_ACHIEVEMENTS)
    ]

    scenario_details_layout = [
        [
            sg.Text("Nr.", s=TEXT_LEN),
            sg.In(key="-SCENARIO_ID-", s=3),
            sg.Checkbox("Gespielt", default=True, key="-SCENARIO_PLAYED-"),
        ],
        [
            sg.Text("Name", s=TEXT_LEN),
            sg.In(key="-SCENARIO_NAME-", s=IN_LEN),
        ],
        [sg.Text("Ziel", s=TEXT_LEN), sg.In(key="-SCENARIO_AIM-", s=IN_LEN)],
        [
            sg.Text("Voraussetzungen", s=TEXT_LEN),
            sg.Listbox(
                values=achievements,
                s=(IN_LEN, min(len(achievements), 5)),
                select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                key="-SCENARIO_REQUIREMENTS-",
                no_scrollbar=True,
            ),
        ],
        [
            sg.Text("Nachfolger", s=TEXT_LEN),
            sg.In(key="-SCENARIO_SUCCESSORS-", s=IN_LEN),
        ],
        [
            sg.Text("Vorgänger", s=TEXT_LEN),
            sg.Text("", key="-SCENARIO_PREDECESSORS-", s=IN_LEN),
        ],
        [
            sg.Text("Schwierigkeitsgrad", s=TEXT_LEN),
            sg.Listbox(
                values=[d.name for d in Difficulty],
                key="-SCENARIO_DIFFICULTY-",
                no_scrollbar=True,
                s=(IN_LEN, len([d.name for d in Difficulty])),
            ),
        ],
        [sg.Text("Anläufe", s=TEXT_LEN), sg.In(s=IN_LEN, key="-SCENARIO_ATTEMPTS-")],
        [
            sg.Text("Belohnungen", s=TEXT_LEN),
            sg.Multiline(key="-SCENARIO_REWARDS-", s=(IN_LEN, 2), no_scrollbar=True),
        ],
        [
            sg.Text("Erfolge", s=TEXT_LEN),
            sg.Button("Hinzufügen", key="-SCENARIO_ACHIEVEMENTS_ADD-"),
        ],
        [
            sg.Column(
                [[l] for l in achievements_layout], key="-SCENARIO_ACHIEVEMENTS-", p=0
            )
        ],
        [sg.Text("Beschreibung")],
        [
            sg.Multiline(
                key="-SCENARIO_DESCRIPTION-",
                no_scrollbar=True,
                s=(int(ROW_WIDTH * 1.05), 5),
            )
        ],
    ]

    scenario_layout = [
        [
            sg.Text("Szenario auswählen"),
            sg.OptionMenu(
                values=manager.short(),
                default_value=manager.short()[0],
                key="-SCENARIO_SELECTOR-",
            ),
            sg.Button("Laden", key="-SCENARIO_LOAD-", s=6),
            sg.Button("Löschen", key="-SCENARIO_DELETE-", s=6),
        ],
        [
            sg.Button("Abgeschlossen", key="-SCENARIO_DONE-", s=11),
            sg.Button("Zurücksetzen", key="-SCENARIO_RESET-", s=11),
            sg.Button("Speichern", key="-SCENARIO_SAVE-", s=11),
        ],
        [sg.Frame("Bearbeiten", scenario_details_layout, key="-SCENARIO_EDIT-")],
    ]

    layout = [
        [sg.Text(APP_NAME, font="default 24", p=((2, 2), (2, 8)))],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Allgemein", general_layout),
                        sg.Tab("Szenario - Details", scenario_layout),
                    ]
                ],
                key="-TAB_GROUP-",
            )
        ],
        [
            sg.Button("Beenden ohne speichern", key="-EXIT-"),
            sg.Button("Beenden mit speichern", key="-EXIT_SAVE-"),
        ],
    ]

    return sg.Window(
        APP_NAME, layout, font=f"Default {FONT_SIZE['default']}"
    ).finalize()


def update_pbar(window, manager):
    window["-PBAR_LOCATIONS_PERCENTAGE-"].update(
        f"{len(manager)}/{config.COUNT_SCENARIOS} ({100 * len(manager) / config.COUNT_SCENARIOS:.2f} %)"
    )
    window["-PBAR_LOCATIONS-"].update_bar(len(manager))

    num_played = len([s for s in manager.values() if s.played])
    window["-PBAR_PLAYED_PERCENTAGE-"].update(
        f"{num_played}/{config.COUNT_SCENARIOS} ({100 * num_played / config.COUNT_SCENARIOS:.2f} %)"
    )
    window["-PBAR_PLAYED-"].update_bar(num_played)


def get_scenario(window, values) -> Scenario:
    id = values["-SCENARIO_ID-"]
    if not id.strip():
        # Return None if no id was provided
        return None
    name = values["-SCENARIO_NAME-"]
    aim = values["-SCENARIO_AIM-"]
    successors = [succ.strip() for succ in values["-SCENARIO_SUCCESSORS-"].split(",")]
    predecessors = [
        pre.split()[1]
        for pre in window["-SCENARIO_PREDECESSORS-"].DisplayText.split(",")
        if len(pre.split()) > 1
    ]
    difficulty = (
        Difficulty[values["-SCENARIO_DIFFICULTY-"][0]]
        if values["-SCENARIO_DIFFICULTY-"]
        else None
    )
    attempts = values["-SCENARIO_ATTEMPTS-"]
    description = values["-SCENARIO_DESCRIPTION-"]
    rewards = values["-SCENARIO_REWARDS-"].split("\n")
    requirements = values["-SCENARIO_REQUIREMENTS-"]
    achievements = []
    for i in range(MAX_ACHIEVEMENTS):
        if (
            window[("-SCENARIO_ACHIEVEMENT-", i)].visible
            and values[("-SCENARIO_ACHIEVEMENT_NAME-", i)].strip()
        ):
            type = values[("-SCENARIO_ACHIEVEMENT_TYPE-", i)]
            status = values[("-SCENARIO_ACHIEVEMENT_STATUS-", i)]
            achievement = Achievement(
                values[("-SCENARIO_ACHIEVEMENT_NAME-", i)],
                AchievementType[type],
                AchievementStatus[status],
            )
            if values[("-SCENARIO_ACHIEVEMENT_CHECK_A-"), i]:
                achievements.append(achievement)
            else:
                requirements.append(achievement)
    played = values["-SCENARIO_PLAYED-"]

    return Scenario(
        id,
        name,
        aim,
        successors,
        predecessors,
        difficulty,
        attempts,
        description,
        rewards,
        achievements,
        requirements,
        played,
    )


def reset_scenario(window):
    window["-SCENARIO_ID-"].update("")
    window["-SCENARIO_NAME-"].update("")
    window["-SCENARIO_AIM-"].update("")
    window["-SCENARIO_SUCCESSORS-"].update("")
    window["-SCENARIO_PREDECESSORS-"].update("")
    window["-SCENARIO_DIFFICULTY-"].update(set_to_index=-1)
    window["-SCENARIO_ATTEMPTS-"].update("")
    window["-SCENARIO_DESCRIPTION-"].update("")
    window["-SCENARIO_REWARDS-"].update("")
    window["-SCENARIO_PLAYED-"].update(True)
    [hide_achievement(window, i) for i in range(MAX_ACHIEVEMENTS)]


def load_scenario(window, manager, scenario):
    reset_scenario(window)
    window["-SCENARIO_ID-"].update(scenario.id)
    window["-SCENARIO_PLAYED-"].update(scenario.played)
    if scenario.name:
        window["-SCENARIO_NAME-"].update(scenario.name)
    if scenario.aim:
        window["-SCENARIO_AIM-"].update(scenario.aim)

    window["-SCENARIO_SUCCESSORS-"].update(", ".join(scenario.successors))
    window["-SCENARIO_PREDECESSORS-"].update(
        str([manager[pre].short_formatted() for pre in scenario.predecessors])
    )
    if scenario.difficulty:
        window["-SCENARIO_DIFFICULTY-"].update(set_to_index=scenario.difficulty.value)
    if scenario.attempts:
        window["-SCENARIO_ATTEMPTS-"].update(scenario.attempts)
    if scenario.description:
        window["-SCENARIO_DESCRIPTION-"].update(scenario.description)
    window["-SCENARIO_REWARDS-"].update("\n".join(scenario.rewards))
    requirements_list = window["-SCENARIO_REQUIREMENTS-"]
    requirements_list.update(
        set_to_index=[
            requirements_list.Values.index(req)
            for req in scenario.requirements
            if req in requirements_list.Values
        ]
    )

    for i, achievement in enumerate(scenario.achievements):
        unhide_achievement(window)
        window[("-SCENARIO_ACHIEVEMENT_NAME-", i)].update(achievement.name)
        window[("-SCENARIO_ACHIEVEMENT_TYPE-", i)].update(achievement.type.name)
        window[("-SCENARIO_ACHIEVEMENT_STATUS-", i)].update(achievement.status.name)


def unhide_achievement(window):
    for i in range(MAX_ACHIEVEMENTS):
        elem = window[("-SCENARIO_ACHIEVEMENT-", i)]
        if not elem.visible:
            elem.update(visible=True)
            break


def hide_achievement(window, i):
    elem = window[("-SCENARIO_ACHIEVEMENT-", i)]
    elem.update(visible=False)
    window[("-SCENARIO_ACHIEVEMENT_NAME-", i)].update("")
    window[("-SCENARIO_ACHIEVEMENT_CHECK_A-", i)].update(True)
    window[("-SCENARIO_ACHIEVEMENT_CHECK_R-", i)].update(False)


def get_scenario_id(values):
    return values["-SCENARIO_SELECTOR-"].split()[1]


def save_world_status(
    window: sg.Window, values: Dict[any, any], manager: ScenarioManager
) -> None:
    manager.world_status = values["-GENERAL_WORLD_STATUS-"]
    add_world_status(window, values, manager)
    manager.to_file(config.SCENARIO_DATABASE)


def add_world_status(
    window: sg.Window, values: Dict[any, any], manager: ScenarioManager
):
    if values["-GENERAL_WORLD_STATUS_NAME-"].strip():
        type = values["-GENERAL_WORLD_STATUS_TYPE-"]
        status = values["-GENERAL_WORLD_STATUS_STATUS-"]
        achievement = Achievement(
            values["-GENERAL_WORLD_STATUS_NAME-"],
            AchievementType[type],
            AchievementStatus[status],
        )
        window["-GENERAL_WORLD_STATUS_NAME-"].update("")
        manager.add_world_status(achievement)


def save_scenario(window: sg.Window, values: Dict[any, any], manager: ScenarioManager):
    scenario = get_scenario(window, values)
    manager.add_scenario(scenario)
    return scenario


def update(window, manager):
    manager.to_file(config.SCENARIO_DATABASE)
    update_pbar(window, manager)


def main():
    manager = ScenarioManager.from_file(config.SCENARIO_DATABASE)
    window = init_window(manager)
    update_pbar(window, manager)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == "-EXIT-" or event == sg.WIN_CLOSED:
            break
        elif event == "-EXIT_SAVE-":
            tab = window["-TAB_GROUP-"].get()
            if tab == "Allgemein":
                save_world_status(window, values, manager)
            elif tab == "Szenario - Details":
                save_scenario(window, values, manager)
                update(window, manager)
            break
        elif event == "-VISUALIZE_RENDER-":
            try:
                manager.render_scenario_tree(
                    config.SCENARIO_TREE,
                    values["-VISUALIZE_SELECTOR-"].split()[1],
                    config.SCENARIO_TREE_FORMAT,
                    config.VISUALIZE_MAX_HOPS,
                )
            except ScenarioNotFoundException as e:
                messagebox.showerror("Fehler", str(e))

        elif event == "-VISUALIZE_RENDER_ALL-":
            manager.render_tree(config.SCENARIO_TREE, config.SCENARIO_TREE_FORMAT)
        elif event == "-SCENARIO_LOAD-":
            scenario_id = get_scenario_id(values)
            load_scenario(window, manager, manager[scenario_id])
        elif event == "-SCENARIO_RESET-":
            reset_scenario(window)
        elif event == "-SCENARIO_ACHIEVEMENTS_ADD-":
            unhide_achievement(window)
        elif isinstance(event, tuple) and event[0] == "-SCENARIO_ACHIEVEMENT_DEL-":
            hide_achievement(window, event[1])
        elif event == "-SCENARIO_SAVE-":
            save_scenario(window, values, manager)
            update(window, manager)
        elif event == "-SCENARIO_DONE-":
            scenario = save_scenario(window, values, manager)
            if scenario:
                scenario.played = True
                window['-SCENARIO_PLAYED-'].update(True)
                [
                    manager.add_world_status(achievement)
                    for achievement in scenario.achievements
                ]
                update(window, manager)
        elif event == "-SCENARIO_DELETE-":
            scenario_id = get_scenario_id(values)
            manager.remove_scenario(scenario_id)
            update(window, manager)
        elif event == "-GENERAL_SAVE-":
            save_world_status(window, values, manager)

    window.close()


if __name__ == "__main__":
    main()
