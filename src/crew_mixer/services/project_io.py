import json
import pathlib

from pydantic import ValidationError

import crew_mixer.domain.data_model as m


def save_project(project: m.Project, filename: pathlib.Path):
    project_json = project.model_dump_json(indent=4)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(project_json)


def load_project(filename: pathlib.Path) -> m.Project:
    with open(filename, "r", encoding="utf-8") as f:
        project_json = f.read()

    # First we verify the schema version
    try:
        raw_json = json.loads(project_json)
    except json.JSONDecodeError as err:
        raise ValueError("Loaded project is not readable json!") from err
        # TODO Error is raised instead of handled

    # check if there is any schema version
    if "schema_version" not in raw_json:
        raise ValueError("Loaded project does not contain a schema version!")
        # TODO Error is raised instead of handled

    # check if there is the right schema version
    if raw_json["schema_version"] != 1:
        raise ValueError("Loaded project schema version is not 1!")
        # TODO Error is raised instead of handled

    # transform the json to a project
    try:
        project = m.Project.model_validate_json(project_json)
    except ValidationError as err:
        raise ValueError("Loaded project does not fit the schema!") from err

    return project
