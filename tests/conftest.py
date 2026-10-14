import uuid
import pytest
from datetime import date, datetime, time, timezone

import crew_mixer.domain.data_model as m


@pytest.fixture
def example_project_empty() -> m.Project:
    """Create a fixture empty project usable in the tests."""
    return m.Project(
        event=m.Event(
            name="Test",
            starting_day=date(year=2420, month=4, day=20),
            days=[],
            volunteers=[],
            pairs=[],
            areas=[],
            shifts=[],
            markers=[],
        )
    )


@pytest.fixture
def example_project_noplan() -> m.Project:
    """Create a fixture example project usable in the tests."""
    volunteer_ids = [uuid.uuid4() for _ in range(12)]
    area_infield_id = uuid.uuid4()
    shift_ids = [uuid.uuid4() for _ in range(12)]  # 3 days a 4 shifts

    return m.Project(
        event=m.Event(
            name="Test",
            starting_day=date(year=2420, month=4, day=20),
            days=[
                m.Day(day_index=0, day_type=m.DayType.SCHEDULED),
                m.Day(day_index=1, day_type=m.DayType.SCHEDULED),
                m.Day(day_index=2, day_type=m.DayType.SCHEDULED),
                m.Day(
                    day_index=3,
                    day_type=m.DayType.TOGETHER,
                    together_text="test_together",
                ),
            ],
            volunteers=[
                m.Volunteer(
                    id=volunteer_ids[i],
                    first_name=f"Volunteer {i}",
                    last_name="Bond",
                    gender=m.Gender.M,
                )
                for i in range(12)
            ],
            pairs=[
                m.Pair(
                    volunteer_a_id=volunteer_ids[0], volunteer_b_id=volunteer_ids[1]
                ),
                m.Pair(
                    volunteer_a_id=volunteer_ids[2], volunteer_b_id=volunteer_ids[3]
                ),
            ],
            areas=[m.Area(id=area_infield_id, name="Infield", color="Red")],
            shifts=[
                m.Shift(
                    id=shift_ids[d * 4 + s],
                    day_index=d,
                    start=time(10, 0),
                    end=time(15, 0),
                    shift_type=[
                        m.ShiftType.MORNING,
                        m.ShiftType.MIDDAY,
                        m.ShiftType.EVENING,
                        m.ShiftType.NIGHT,
                    ][s],
                    area_id=area_infield_id,
                    desired_volunteers=3,
                )
                for d in range(3)
                for s in range(4)
            ],
            markers=[
                m.Marker(
                    day_index=0,
                    start=time(15, 0),
                    end=time(17, 0),
                    note="TestMarker",
                )
            ],
        )
    )


@pytest.fixture
def example_project_plan(example_project_noplan) -> m.Project:
    """Create a fixture example project usable in the tests."""
    project = example_project_noplan
    project.plan = m.Plan(
        assignments=[
            m.Assignment(
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
