import crew_mixer.domain.data_model as m
from datetime import datetime, timezone
from ortools.sat.python import cp_model

import crew_mixer.solver.hard_constraints as hc


def solve(event: m.Event, seed: int | None = None) -> m.SolveResult:
    """Tries to find a schedule for the event.

    The seed argument should not be used and it only for testing.
    """
    model = cp_model.CpModel()

    # Variables
    assign = {}
    for v in event.volunteers:
        for s in event.shifts:
            assign[v.id, s.id] = model.new_bool_var(
                f"Volunteer {v.first_name} (id: {v.id}) is part of shift {s.id}."
            )

    # hard constraints
    flips = {}
    flip_all_shifts_filled = model.new_bool_var("flip_all_shifts_filled")
    flips[flip_all_shifts_filled.index] = flip_all_shifts_filled.name
    hc.add_constraint_all_shifts_filled(event, model, assign, flip_all_shifts_filled)

    flip_one_shift_per_day = model.new_bool_var("flip_one_shift_per_day")
    flips[flip_one_shift_per_day.index] = flip_one_shift_per_day.name
    hc.add_constraint_one_shift_per_day(event, model, assign, flip_one_shift_per_day)

    flip_no_morning_after_night_shift = model.new_bool_var(
        "flip_no_morning_after_night_shift"
    )
    flips[flip_no_morning_after_night_shift.index] = (
        flip_no_morning_after_night_shift.name
    )
    hc.add_constraint_no_morning_after_night_shift(
        event, model, assign, flip_no_morning_after_night_shift
    )

    model.add_assumptions(
        [
            flip_all_shifts_filled,
            flip_one_shift_per_day,
            flip_no_morning_after_night_shift,
        ]
    )

    # soft constraints
    # TODO

    # Solve
    solver = cp_model.CpSolver()

    if seed is not None and type(seed) is int:
        solver.parameters.random_seed = seed
        solver.parameters.num_workers = 1

    # Print the solver status
    status_code = solver.solve(model)

    if status_code not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        safi = solver.sufficient_assumptions_for_infeasibility()

        return m.SolveResult(
            plan=None,
            problems=[
                m.Problem(
                    code=m.ProblemCode.NO_PLAN_FOUND,
                    data=f"The solver could not find a fitting plan. It returned {status_code.name} ({status_code}). Assumptions: {[flips[i] for i in safi]}!",
                )
            ],
        )
    else:
        # Construct plan from solver
        plan = m.Plan(
            score=0,  # TODO
            created_at=datetime.now(timezone.utc),
        )

        for s in event.shifts:
            # collect all assigned volunteers for this shift
            assigned_volo_ids = [
                v.id for v in event.volunteers if solver.value(assign[v.id, s.id])
            ]

            plan.assignments.append(
                m.Assignment(
                    shift_id=s.id,
                    volunteer_ids=assigned_volo_ids,
                )
            )

        return m.SolveResult(plan=plan, problems=[])
