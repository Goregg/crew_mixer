import crew_mixer.services.project_io as service


def test_round_trip(example_project_plan, tmp_path):
    """Converts the project model to json and back."""
    service.save_project(example_project_plan, tmp_path / "test_round_trip.json")
    again = service.load_project(tmp_path / "test_round_trip.json")

    assert again == example_project_plan


# test_error_on_loading_none_json()
# test_error_on_loading_wrong_schema_version()
# test_error_on_loading_damaged_project()
