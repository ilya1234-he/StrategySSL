import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


def kick_goal(field: fld.Field, actions: list[Optional[Action]], kicker: int) -> None:
    if (field.allies[kicker].get_pos()).mag() < (field.enemy_goal.frw).mag():
        if field.enemies[field.enemy_gk_id].get_pos().y < 0:
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


def defend_goal_ally(field: fld.Field, actions: list[Optional[Action]]) -> None:
    defender = field.gk_id

    if not aux.is_point_inside_poly(field.ball.get_pos(), field.hull):
        inter_point = aux.get_line_intersection(
            field.ball_start_point,
            field.ball.get_pos(),
            aux.Point(field.ally_goal.frw_up.x - 200, field.ally_goal.frw_up.y + 500),
            aux.Point(field.ally_goal.frw_down.x - 200, field.ally_goal.frw_down.y + 500),
            "LS",
        )
        if inter_point is None:
            inter_point = field.ally_goal.center

        actions[defender] = Actions.GoToPoint(inter_point, (field.ball.get_pos() - field.allies[defender].get_pos()).arg())
    else:
        print(field.ball.get_pos())
        a = [defender]
        day_pas(field, actions, defender, fld.find_nearest_robot(field.ball.get_pos(), field.allies, a).r_id, 600)

    # actions[defender] = Actions.GoToPoint(field.ally_goal.center, (field.ball.get_pos()).arg())


# in_place(field.ball.get_pos(), field.allies[defender].get_pos(), 500)


def day_pas(field: fld.Field, actions: list[Optional[Action]], kicker: int, accepter: int, rastt: float) -> None:
    if rastt == -1:
        rastt = (field.allies[accepter].get_pos() - field.ball.get_pos()).mag()
    if aux.in_place(field.ball.get_pos(), field.allies[accepter].get_pos(), 500):
        actions[accepter] = Actions.Kick(field.enemy_goal.center)
    else:
        if not aux.in_place(field.ball.get_pos(), field.allies[kicker].get_pos(), 1000):
            accept_point = ((field.allies[accepter].get_pos() - field.ball.get_pos()).unity() * rastt) + field.ball.get_pos()

        actions[accepter] = Actions.GoToPoint(accept_point, (field.ball.get_pos() - field.allies[accepter].get_pos()).arg())
        actions[kicker] = Actions.Kick(accept_point, is_pass=True)
