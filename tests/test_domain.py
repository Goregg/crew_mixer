import uuid

import pytest

import crew_mixer.domain.data_model as model


# def test_no_self_pair():
#     """Tries to create a pair with the same volunteer."""
#     test_uuid = uuid.uuid4()

#     # with pytest.raises(Exception) as exc_info:
#     #     model.Pair(volunteer_a_id=test_uuid, volunteer_b_id=test_uuid)


# def test_shift_start_before_end():
#     """Tries to create a shift which ends before it starts."""
#     # TODO
