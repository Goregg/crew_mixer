from collections import defaultdict
from datetime import date, time
import uuid

import crew_mixer.domain.data_model as m
import crew_mixer.solver.solver as solver


def test_solve_no_errors(example_project_noplan):
    event = example_project_noplan.event

    solve_results = solver.solve(event)

    # was a plan without errors returned?
    assert solve_results.plan is not None
    assert solve_results.problems == []


def test_solve_constraint_all_shifts_filled(example_project_noplan):
    event = example_project_noplan.event

    solve_results = solver.solve(event)

    assert solve_results.plan is not None

    assigned_volunteers_per_shift = {}
    for a in solve_results.plan.assignments:
        assigned_volunteers_per_shift[a.shift_id] = a.volunteer_ids

    for s in event.shifts:
        # for each shift the number of desired volunteers should match the number of assigned volunteers
        assert s.desired_volunteers == len(assigned_volunteers_per_shift[s.id])


def test_solve_constraint_one_shift_per_day(example_project_noplan):
    event = example_project_noplan.event

    solve_results = solver.solve(event)

    assert solve_results.plan is not None

    assigned_volunteers_per_shift = {}
    for a in solve_results.plan.assignments:
        assigned_volunteers_per_shift[a.shift_id] = a.volunteer_ids

    shifts_by_day = defaultdict(list)
    for s in event.shifts:
        shifts_by_day[s.day_index].append(s)

    for d in example_project_noplan.event.days:
        if d.day_type == m.DayType.SCHEDULED:
            assigned_volunteers = []

            # collect the volunteers assigned to each shift
            for s in shifts_by_day[d.day_index]:
                assigned_volunteers.extend(assigned_volunteers_per_shift[s.id])

            # check if there are any duplicates
            assert len(assigned_volunteers) == len(set(assigned_volunteers))


def test_solve_constraint_no_morning_after_night_shift(example_project_noplan):
    event = example_project_noplan.event

    solve_results = solver.solve(event)

    assert solve_results.plan is not None

    assigned_volunteers_per_shift = {}
    for a in solve_results.plan.assignments:
        assigned_volunteers_per_shift[a.shift_id] = a.volunteer_ids

    shifts_by_day = defaultdict(list)
    for s in event.shifts:
        shifts_by_day[s.day_index].append(s)

    # add_constraint_no_morning_after_night_shift()
    for d in example_project_noplan.event.days:
        if d.day_type == m.DayType.SCHEDULED:
            for s_n in shifts_by_day[d.day_index]:
                if s_n.shift_type == m.ShiftType.NIGHT:
                    for s_m in shifts_by_day[d.day_index + 1]:
                        if s_m.shift_type == m.ShiftType.MORNING:
                            # when a morning shift following a night shift is found the assigned volunteers are checked
                            assigned_volunteers = []

                            assigned_volunteers.extend(
                                assigned_volunteers_per_shift[s_n.id]
                            )
                            assigned_volunteers.extend(
                                assigned_volunteers_per_shift[s_m.id]
                            )

                            # check if there are any duplicates
                            assert len(assigned_volunteers) == len(
                                set(assigned_volunteers)
                            )


def test_error_only_morning_after_night():
    area_infield_id = uuid.uuid4()

    # create an event with a only a morning shift following a night shift
    event = m.Event(
        name="Test",
        starting_day=date(year=2420, month=4, day=20),
        days=[
            m.Day(day_index=0, day_type=m.DayType.SCHEDULED),
            m.Day(day_index=1, day_type=m.DayType.SCHEDULED),
        ],
        volunteers=[
            m.Volunteer(
                first_name="VolunteerA",
                last_name="Bond",
                gender=m.Gender.M,
            ),
        ],
        areas=[m.Area(id=area_infield_id, name="Infield", color="Red")],
        shifts=[
            m.Shift(
                day_index=0,
                start=time(20, 0),
                end=time(1, 0),
                shift_type=m.ShiftType.NIGHT,
                area_id=area_infield_id,
                desired_volunteers=1,
            ),
            m.Shift(
                day_index=1,
                start=time(6, 0),
                end=time(11, 0),
                shift_type=m.ShiftType.MORNING,
                area_id=area_infield_id,
                desired_volunteers=1,
            ),
        ],
    )

    solve_results = solver.solve(event)

    assert solve_results.plan is None
    assert solve_results.problems[0].code == m.ProblemCode.NO_PLAN_FOUND
    assert "flip_no_morning_after_night_shift" in solve_results.problems[0].data


def test_error_unsolvable_event(example_project_noplan):
    event = example_project_noplan.event
    event.volunteers.append(
        m.Volunteer(
            first_name="VolunteerC",
            last_name="Degree",
            gender=m.Gender.W,
        )
    )

    solve_results = solver.solve(event)

    assert solve_results.plan is None
    assert solve_results.problems[0].code == m.ProblemCode.NO_PLAN_FOUND


def test_reproducibility(example_project_noplan):
    event = example_project_noplan.event

    solve_results = solver.solve(event, seed=42)
    solve_results2 = solver.solve(event, seed=42)

    assert solve_results.plan is not None
    assert solve_results2.plan is not None
    assert solve_results.plan.assignments == solve_results2.plan.assignments
