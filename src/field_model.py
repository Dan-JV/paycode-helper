"""The classes in this file are used to define and verify the structure of the form and feedback templates."""

import yaml
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Literal


class FieldModel(BaseModel):
    name: str
    front_end_name: str
    type: Literal[
        "text_input",
        "selectbox",
        "text_area",
        "multiselect",
        "tags",
        "write",
        "toggle",
        "markdown",
        "bool_Ja_Nej",
        "radio",
    ]
    placeholder: Optional[str] = None
    help: Optional[str] = None
    input: Optional[str] = None
    options: Optional[List[str]] = None
    catalog_name: Optional[str] = None


class AreaModel(BaseModel):
    name: str
    description: str
    fields: List[FieldModel]


class FormTemplateModel(BaseModel):
    name: str
    description: str
    areas: List[AreaModel]


class FeedbackTemplateModel(BaseModel):
    name: str
    description: str
    fields: List[FieldModel]


class VerificationTemplateModel(BaseModel):
    name: str
    description: str
    areas: List[AreaModel]


class TemplateModel(BaseModel):
    form_template: FormTemplateModel
    feedback_template: FeedbackTemplateModel
    verification_template: VerificationTemplateModel


def load_template(file_path: str) -> TemplateModel:
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    try:
        return TemplateModel(**data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None
