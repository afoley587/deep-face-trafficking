from concurrent.futures import ThreadPoolExecutor
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
                logger.info("FOUND POSSIBLE!")


def search_namus(original, race=None, age=None, gender=None, emotion=None):
    logger.info("SEARCH NAMUS")
    search_api = NAMUS_BASE + "/api/CaseSets/NamUs/MissingPersons/Search"

    headers = {"Content-Type": "application/json; charset=utf-8"}

    predicates = []

    if race is not None:
        race = race.lower()
        if race == "white":
            race = "White / Caucasian"

        predicates.append(
            NamusPayloadPredicate(
                field="ethnicities",
                operator="Matches",
                predicates=[
                    NamusPayloadSubPredicate(
                        field="raceEthnicity", operator="IsIn", values=[race]
                    )
                ],
            )
        )

    if age is not None:
        age = int(age)
        lower_bound = age - 5
        upper_bound = age + 5
        predicates.append(
            NamusPayloadPredicate(
                field="currentAge",
                operator="Between",
                from_=lower_bound,
                to=upper_bound,
            )
        )

    if gender is not None:
        if gender.lower() == "woman":
            gender = "Female"
        else:
            gender = "Male"

        predicates.append(
            NamusPayloadPredicate(
                field="gender",
                operator="IsIn",
                values=[gender],
            )
        )

    payload = NamusPayload(take=1, predicates=predicates).model_dump_json(
        by_alias=True, exclude_none=True
    )
    r = requests.post(search_api, headers=headers, data=payload)
    matches = None
    logger.info(r)
    logger.info(payload)
    if not r.ok:
        logger.info(r)
        logger.info(payload)
    else:
        _json = r.json()
        logger.info(_json)
        matches = NamusResponse(**_json)

    if matches is not None:
        cp = NamusFaceComparator()
        cp.run_analysis(matches.results, original)


if __name__ == "__main__":
    search_namus(
        "/Users/alexanderfoley/mycode/traffic-detection/trafficdetection/test-images/test.jpg",
        race="white",
        age=15,
        gender="male",
    )
