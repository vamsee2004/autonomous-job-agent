import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)

PROFILE_PATH = Path(
    "app/knowledge/candidate_profile.json"
)


@router.get("/")
def get_candidate():

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        profile = json.load(file)

    return profile
