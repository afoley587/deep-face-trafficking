from concurrent.futures import ThreadPoolExecutor
import shutil
import tempfile

import requests
from deepface import DeepFace

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
        print("In _run_analysis")
        print(result)
        if not self.is_running:
            return False

        url = NAMUS_BASE + result.image
        response = requests.get(url, stream=True)
        tmp = tempfile.NamedTemporaryFile(suffix=".png")

        print(tmp.name)
        with open(tmp.name, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)

        result = DeepFace.verify(
            img1_path=tmp.name, img2_path=original_image, enforce_detection=False
        )

        print("Result is:", result)
        if result["verified"]:
            # self.running = False
            return result

        return False

    def run_analysis(self, results, original):
        self.is_running = True
        futures = []
        for result in results:
            futures.append(self.tpe.submit(self._run_analysis, result, original))

        for future in futures:
            res = future.result()
            print("Future returned: ", res)
            if (res is not None) and (res == True):
                print("FOUND POSSIBLE!")


def search_namus(original, race=None, age=None, gender=None, emotion=None):
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
        gender = gender.title()
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

    if not r.ok:
        print(r)
        print(payload)
    else:
        _json = r.json()
        # print(_json)
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
