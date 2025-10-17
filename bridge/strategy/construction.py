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
    allies_pos = []
    defender = field.gk_id

    if not aux.in_place(field.ball.get_pos(), field.allies[defender].get_pos(), 500):
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
        for i in field.active_allies():
            allies_pos.append(i.get_pos()) 
        accepter = aux.find_nearest_point(field.allies[defender].get_pos(), allies_pos)

        for i in field.active_allies():
            if accepter == i.get_pos():
                accepter_id = i.r_id

        actions[defender] = Actions.Kick(accepter, is_pass=True)
        
        kick_goal(field, actions, accepter_id)
        # actions[defender] = Actions.GoToPoint(field.ally_goal.center, (field.ball.get_pos() - accepter).arg())
       
