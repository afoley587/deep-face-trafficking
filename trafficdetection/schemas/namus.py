from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field


class NamusPayloadPredicateBase(BaseModel):
    field: str
    operator: str
    value: Optional[Union[int, str, None]] = None
    values: Optional[List[Union[int, str, None]]] = None
    from_: Optional[Union[int, None]] = Field(default=None, alias="from")
    to: Optional[Union[int, None]] = None

    class Config:
        populate_by_name = True


class NamusPayloadSubPredicate(NamusPayloadPredicateBase):
    pass


class NamusPayloadPredicate(NamusPayloadPredicateBase):
    predicates: Optional[List[Union[NamusPayloadSubPredicate, None]]] = None


class NamusResponseItem(BaseModel):
    idFormatted: str
    dateOfLastContact: str
    lastName: str
    firstName: str
    computedMissingMinAge: int
    computedMissingMaxAge: int
    cityOfLastContact: str
    countyDisplayNameOfLastContact: str
    stateDisplayNameOfLastContact: str
    gender: str
    raceEthnicity: Union[str, List[str]]
    modifiedDateTime: str
    namus2Number: int
    link: str
    image: str
    currentAgeFrom: int
    currentAgeTo: int
    missingAgeRangeValue: str


class NamusResponse(BaseModel):
    count: int
    results: List[NamusResponseItem]


class NamusPayload(BaseModel):
    """Example
    {
    "predicates": [
        {
        "field": "computedMissingMinAge",
        "operator": "LessThanOrEqualTo",
        "value": 35
        },
        {
        "field": "computedMissingMaxAge",
        "operator": "GreaterThanOrEqualTo",
        "value": 25
        },
        {
        "field": "gender",
        "operator": "IsIn",
        "values": [
            "Male"
        ]
        }
    ],
    "take": 25,
    "skip": 0,
    "projections": [
        "idFormatted",
        "dateOfLastContact",
        "lastName",
        "firstName",
        "computedMissingMinAge",
        "computedMissingMaxAge",
        "cityOfLastContact",
        "countyDisplayNameOfLastContact",
        "stateDisplayNameOfLastContact",
        "gender",
        "raceEthnicity",
        "modifiedDateTime",
        "namus2Number"
    ],
    "orderSpecifications": [
        {
        "field": "dateOfLastContact",
        "direction": "Descending"
        }
    ],
    "documentFragments": [
        "birthDate"
    ]
    }
    """

    take: int = 25
    skip: int = 0
    projections: List[str] = [
        "idFormatted",
        "dateOfLastContact",
        "lastName",
        "firstName",
        "computedMissingMinAge",
        "computedMissingMaxAge",
        "cityOfLastContact",
        "countyDisplayNameOfLastContact",
        "stateDisplayNameOfLastContact",
        "gender",
        "raceEthnicity",
        "modifiedDateTime",
        "namus2Number",
    ]
    orderSpecifications: List[Dict[str, str]] = [
        {"field": "dateOfLastContact", "direction": "Descending"}
    ]
    documentFragments: List[str] = ["birthDate"]
    predicates: List[NamusPayloadPredicate]  # Only one that doesnt need a default
