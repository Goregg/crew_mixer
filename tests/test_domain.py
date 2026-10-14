import crew_mixer.domain.data_model as m
import crew_mixer.domain.checks as checks


# def test_no_self_pair():
#     """Tries to create a pair with the same volunteer."""
#     test_uuid = uuid.uuid4()

#     # with pytest.raises(Exception) as exc_info:
#     #     model.Pair(volunteer_a_id=test_uuid, volunteer_b_id=test_uuid)


# def test_shift_start_before_end():
#     """Tries to create a shift which ends before it starts."""
#     # TODO Shifts going over midnight must be caught seperatly.


def test_no_error_on_fitting_volunteers_per_shift(example_project_noplan):
    problems = checks.check_day_capacity(example_project_noplan.event)

    assert len(problems) == 0


def test_error_to_many_volunteers_per_shift(example_project_noplan):
    event = example_project_noplan.event
    event.volunteers.append(
        m.Volunteer(
            first_name="VolunteerC",
            last_name="Degree",
            gender=m.Gender.W,
        )
    )
    problems = checks.check_day_capacity(event)

    # function returns one problem for each scheduled day where there are to many volunteers
    assert len(problems) == len(
        [
            d
            for d in example_project_noplan.event.days
            if d.day_type == m.DayType.SCHEDULED
        ]
    )
    assert problems[0].code == m.ProblemCode.TOO_MANY_VOLUNTEERS


def test_error_to_little_volunteers_per_shift(example_project_noplan):
    event = example_project_noplan.event
    event.volunteers = [
        m.Volunteer(
            first_name="VolunteerA",
            last_name="Degree",
            gender=m.Gender.W,
        )
    ]
    problems = checks.check_day_capacity(event)

    # function returns one problem for each scheduled day where there are to many volunteers
    assert len(problems) == len(
        [
            d
            for d in example_project_noplan.event.days
            if d.day_type == m.DayType.SCHEDULED
        ]
    )
    assert problems[0].code == m.ProblemCode.NOT_ENOUGH_VOLUNTEERS
