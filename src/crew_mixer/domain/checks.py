from collections import defaultdict
import crew_mixer.domain.data_model as m
from crew_mixer.domain.data_model import Event, Problem, ProblemCode


def check_day_capacity(event: Event) -> list[Problem]:
    """Calculate the total number of volunteers needed for each day and checks if it matches the number of volunteers."""
    shifts_by_day = defaultdict(list)
    for s in event.shifts:
        shifts_by_day[s.day_index].append(s)

    desired_volunteers_by_day = {}
    for d in event.days:
        # skip together days as there are no shifts
        if d.day_type == m.DayType.TOGETHER:
            continue

        desired_volunteers_by_day[d.day_index] = sum(
            s.desired_volunteers for s in shifts_by_day[d.day_index]
        )

    problems = []

    for d in event.days:
        if d.day_type == m.DayType.SCHEDULED:
            if desired_volunteers_by_day[d.day_index] < len(event.volunteers):
                problems.append(
                    Problem(
                        code=ProblemCode.TOO_MANY_VOLUNTEERS,
                        data=f"There are {len(event.volunteers)} volunteers but the desired volunteers for day {d.day_index} is {desired_volunteers_by_day[d.day_index]}!",
                    )
                )
            if desired_volunteers_by_day[d.day_index] > len(event.volunteers):
                problems.append(
                    Problem(
                        code=ProblemCode.NOT_ENOUGH_VOLUNTEERS,
                        data=f"There are {len(event.volunteers)} volunteers but the desired volunteers for day {d.day_index} is {desired_volunteers_by_day[d.day_index]}!",
                    )
                )

    return problems
