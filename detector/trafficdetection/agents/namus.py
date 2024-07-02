from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Union
import shutil
import tempfile

from deepface import DeepFace
from loguru import logger
import requests

from schemas.namus import (
    NamusPayloadPredicate,
    NamusPayloadSubPredicate,
    NamusPayload,
    NamusResponse,
)

NAMUS_BASE = "https://www.namus.gov"


class NamusFaceComparator:
    def __init__(self):
        self.tpe = ThreadPoolExecutor(max_workers=10)
        self.is_running = False

    def _run_analysis(self, result, original_image):
        if not self.is_running:
            return None

        url = NAMUS_BASE + result.image
        response = requests.get(url, stream=True)
        tmp = tempfile.NamedTemporaryFile(suffix=".png")

        with open(tmp.name, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)

        verif = DeepFace.verify(
            img1_path=tmp.name, img2_path=original_image, enforce_detection=False
        )

        logger.info(f"Result is: {verif}")

        if verif["verified"]:
            return result

        return None

    def run_analysis(self, results, original):
        self.is_running = True
        futures = []
        for result in results:
            futures.append(self.tpe.submit(self._run_analysis, result, original))

        for future in futures:
            res = future.result()
            logger.info(f"Future returned: {res}")
            if res is not None:
                self.running = False
                return res


class NamusSearchAgent:
    def __init__(self):
        self.api_headers: Dict[str, str] = {
            "Content-Type": "application/json; charset=utf-8"
        }
        self.api_path: str = "/api/CaseSets/NamUs/MissingPersons/Search"

    def _get_race(self, race: str) -> str:
        _races = {"white": "White / Caucasian"}
        return _races[race.lower()]

    def _get_gender(self, gender: str) -> str:
        _genders = {"woman": "Female", "man": "Male"}
        return _genders[gender.lower()]

    def search_victims(self, frame, victims: List[Dict[Any, Any]]):
        for v in victims:
            self.search(frame, **v)

    def search(
        self,
        original,
        race: Union[str, None] = None,
        age: Union[str, None] = None,
        gender: Union[str, None] = None,
        emotion: Union[str, None] = None,
    ):
        logger.info("SEARCH NAMUS")
        search_api = NAMUS_BASE + self.api_path

        predicates = []

        if race is not None:
            normalized_race = self._get_race(race)

            predicates.append(
                NamusPayloadPredicate(
                    field="ethnicities",
                    operator="Matches",
                    predicates=[
                        NamusPayloadSubPredicate(
                            field="raceEthnicity",
                            operator="IsIn",
                            values=[normalized_race],
                        )
                    ],
                )
            )

        if age is not None:
            age_ = int(age)
            lower_bound = age_ - 5
            upper_bound = age_ + 5
            predicates.append(
                NamusPayloadPredicate(
                    field="currentAge",
                    operator="Between",
                    from_=lower_bound,
                    to=upper_bound,
                )
            )

        if gender is not None:
            normalized_gender = self._get_gender(gender)

            predicates.append(
                NamusPayloadPredicate(
                    field="gender",
                    operator="IsIn",
                    values=[normalized_gender],
                )
            )

        payload = NamusPayload(take=1, predicates=predicates).model_dump_json(
            by_alias=True, exclude_none=True
        )
        r = requests.post(search_api, headers=self.api_headers, data=payload)
        matches = None
        logger.info(r)
        logger.info(payload)
        if not r.ok:
            logger.error(r)
            logger.error(payload)
            return
        else:
            json_ = r.json()
            logger.info(json_)
            matches = NamusResponse(**json_)

        if matches is not None:
            cp = NamusFaceComparator()
            possible = cp.run_analysis(matches.results, original)
