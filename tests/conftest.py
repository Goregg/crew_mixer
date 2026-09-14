import uuid
import pytest
from datetime import date, datetime, time, timezone

import crew_mixer.domain.data_model as model


@pytest.fixture
def example_project_noplan() -> model.Project:
    """Create a fixture example project usable in the tests."""
    volunteer_a_id = uuid.uuid4()
    volunteer_b_id = uuid.uuid4()
    area_infield_id = uuid.uuid4()
    shift_id = uuid.uuid4()

    return model.Project(
        event=model.Event(
            name="Test",
            starting_day=date(year=2420, month=4, day=20),
            days=[model.Day(date_index=0, day_type=model.DayType.SCHEDULED)],
            volunteers=[
                model.Volunteer(
                    id=volunteer_a_id,
                    first_name="VolunteerA",
                    last_name="Bond",
                    gender=model.Gender.M,
                ),
                model.Volunteer(
                    id=volunteer_b_id,
                    first_name="VolunteerB",
                    last_name="Degree",
                    gender=model.Gender.W,
                ),
            ],
            pairs=[
                model.Pair(volunteer_a_id=volunteer_a_id, volunteer_b_id=volunteer_b_id)
            ],
            areas=[model.Area(id=area_infield_id, name="Infield", color="Red")],
            shifts=[
                model.Shift(
                    id=shift_id,
                    day_index=0,
                    start=time(10, 0),
                    end=time(15, 0),
                    shift_type=model.ShiftType.MIDDAY,
                    area_id=area_infield_id,
                    desired_volunteers=2,
                )
            ],
            markers=[
                model.Marker(
                    day_index=0,
                    start=time(15, 0),
                    end=time(17, 0),
                    note="TestMarker",
                )
            ],
        )
    )


@pytest.fixture
def example_project_plan(example_project_noplan) -> model.Project:
    """Create a fixture example project usable in the tests."""
    project = example_project_noplan
    project.plan = model.Plan(
        assignments=[
            model.Assignment(
                shift_id=project.event.shifts[0].id,
                volunteer_ids=[
                    project.event.volunteers[0].id,
                    project.event.volunteers[1].id,
                ],
            )
        ],
        score=0,
        created_at=datetime.now(timezone.utc),
    )
    return project
