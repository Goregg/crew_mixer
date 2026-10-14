from collections import defaultdict

import crew_mixer.domain.data_model as m
import uuid
from ortools.sat.python import cp_model


def add_constraint_all_shifts_filled(
    event: m.Event,
    model: cp_model.CpModel,
    assign: dict[tuple[uuid.UUID, uuid.UUID], cp_model.IntVar],
    flip: cp_model.IntVar,
):
    for s in event.shifts:
        model.add(
            sum(assign[v.id, s.id] for v in event.volunteers) == s.desired_volunteers
        ).only_enforce_if(flip)


def add_constraint_one_shift_per_day(
    event: m.Event,
    model: cp_model.CpModel,
    assign: dict[tuple[uuid.UUID, uuid.UUID], cp_model.IntVar],
    flip: cp_model.IntVar,
):
    shifts_by_day = defaultdict(list)
    for s in event.shifts:
        shifts_by_day[s.day_index].append(s)

    for d in event.days:
        # skip together days as there are no shifts
        if d.day_type == m.DayType.TOGETHER:
            continue

        for v in event.volunteers:
            model.add_exactly_one(
                [assign[v.id, s.id] for s in shifts_by_day[d.day_index]]
            ).only_enforce_if(flip)


def add_constraint_no_morning_after_night_shift(
    event: m.Event,
    model: cp_model.CpModel,
    assign: dict[tuple[uuid.UUID, uuid.UUID], cp_model.IntVar],
    flip: cp_model.IntVar,
):
    shifts_by_type = defaultdict(list)
    for s in event.shifts:
        shifts_by_type[s.shift_type].append(s)

    for n_s in shifts_by_type[m.ShiftType.NIGHT]:
        for m_s in shifts_by_type[m.ShiftType.MORNING]:
            # check for each morning shift if it is on the day after the night shift
            # This will 'overflow' but as day_index is an int it does not matter
            if n_s.day_index + 1 == m_s.day_index:
                # Check for each volunteer that they are not part of both shifts
                for v in event.volunteers:
                    model.add_at_most_one(
                        [assign[v.id, n_s.id], assign[v.id, m_s.id]]
                    ).only_enforce_if(flip)
