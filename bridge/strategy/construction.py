import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


def kick_goal(field: fld.Field, actions: list[Optional[Action]], kicker: int) -> None:
    if (field.allies[kicker].get_pos()).mag() < (field.enemy_goal.frw).mag():
        if field.enemies[2].get_pos().y < 0:
            actions[kicker] = Actions.Kick(field.enemy_goal.up - (field.enemy_goal.eye_up * 100))
        else:
            actions[kicker] = Actions.Kick(field.enemy_goal.down - (field.enemy_goal.eye_up * (-100)))
    else:
        if field.allies[kicker].get_pos().y < 0:
            actions[kicker] = Actions.Kick(
                field.enemy_goal.up - (field.enemy_goal.eye_up * 100) + (field.enemy_goal.eye_forw * (-150))
            )
        else:
            actions[kicker] = Actions.Kick(
                field.enemy_goal.down - (field.enemy_goal.eye_up * (-100)) + (field.enemy_goal.eye_forw * (-150))
            )


def defend_goal(field: fld.Field, actions: list[Optional[Action]]) -> None:
    allies_pos = [
        field.allies[0].get_pos(),
        field.allies[1].get_pos(),
        field.allies[2].get_pos(),
        field.allies[3].get_pos(),
        field.allies[4].get_pos(),
    ]
    for i in range(3):
        if allies_pos[i] == aux.find_nearest_point(field.ally_goal.center, allies_pos):
            defender = i

    if not aux.in_place(field.ball.get_pos(), field.allies[defender].get_pos(), 500):
        inter_point = aux.get_line_intersection(
            field.ball_start_point,
            field.ball.get_pos(),
            aux.Point(field.ally_goal.frw_up.x - 500, field.ally_goal.frw_up.y),
            aux.Point(field.ally_goal.frw_down.x - 500, field.ally_goal.frw_down.y),
            "LS",
        )
        if inter_point is None:
            inter_point = field.ally_goal.center

        actions[defender] = Actions.GoToPoint(inter_point, (field.ball.get_pos() - field.allies[defender].get_pos()).arg())
    else:
        allies_pos = [field.allies[0].get_pos(), field.allies[1].get_pos(), field.allies[2].get_pos()]
        actions[defender] = Actions.Kick(aux.find_nearest_point(field.allies[defender].get_pos(), allies_pos))
