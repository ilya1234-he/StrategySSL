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


def is_ball_moving(field: fld.Field, ball_speed: float) -> bool:
    return field.ball.get_vel().mag() > 25


def is_ball_in_zone(field: fld.Field) -> bool:
    return aux.is_point_inside_poly(field.ball.get_pos(), field.ally_goal.hull)


def defend_goal_ally(field: fld.Field, actions: list[Optional[Action]]) -> None:
    defender = field.gk_id
    ball_speed = field.ball.get_vel().mag()

    print("Ball: ", field.ball.get_pos(), " b.speed: ", ball_speed)
    if is_ball_in_zone(field):
        print("ball in zone")

    if not is_ball_in_zone(field) or (is_ball_moving(field, ball_speed)):
        inter_point = aux.get_line_intersection(
            field.ball_start_point,
            field.ball.get_pos(),
            aux.Point(field.ally_goal.frw_up.x - 400, field.ally_goal.frw_up.y + 500),
            aux.Point(field.ally_goal.frw_down.x - 400, field.ally_goal.frw_down.y + 500),
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

accept_point: Optional[aux.Point] = None


def day_pas(field: fld.Field, actions: list[Optional[Action]], kicker: int, accepter: int, rastt: float) -> None:
    global accept_point
    reseiving_pas_bound = [
        aux.Point(field.ally_goal.center_up.x, field.ally_goal.center_up.y + (field.ally_goal.eye_up.y * 350)),
        aux.Point(
            field.ally_goal.frw_up.x + (field.ally_goal.eye_forw.x * 350),
            field.ally_goal.frw_up.y + (field.ally_goal.eye_up.y * 350),
        ),
        aux.Point(
            field.ally_goal.frw_down.x + (field.ally_goal.eye_forw.x * 350),
            field.ally_goal.frw_down.y - (field.ally_goal.eye_up.y * 350),
        ),
        aux.Point(field.ally_goal.center_down.x, field.ally_goal.center_down.y - (field.ally_goal.eye_up.y * 350)),
    ]

    field.strategy_image.draw_poly(reseiving_pas_bound, (255, 255, 255), 5)

    if rastt == -1:
        rastt = (field.allies[accepter].get_pos() - field.ball.get_pos()).mag()
    if aux.in_place(field.ball.get_pos(), field.allies[accepter].get_pos(), 300) and (
        not aux.nearest_point_in_poly(field.allies[accepter].get_pos(), reseiving_pas_bound)
    ):
        actions[accepter] = Actions.Kick(field.enemy_goal.center)
    else:
        if accept_point is None or not aux.in_place(field.ball.get_pos(), field.allies[kicker].get_pos(), 1000):
            accept_point = ((field.allies[accepter].get_pos() - field.ball.get_pos()).unity() * rastt) + field.ball.get_pos()

        actions[accepter] = Actions.GoToPoint(accept_point, (field.ball.get_pos() - field.allies[accepter].get_pos()).arg())
        actions[kicker] = Actions.Kick(accept_point, is_pass=True)
