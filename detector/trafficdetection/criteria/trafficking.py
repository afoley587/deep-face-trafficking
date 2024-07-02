from typing import List, Any

def is_possible_trafficking(results: List[Any]) -> bool:
    """Takes the results from a frame and then checks
    to see if any of the sensitive criteria is met.

    Takes a results array from python deepface and
    for each result, if a criteria is met, returns true.
    TODO: Standardize the resutls array type
    """
    kid_age_threshold = 60
    for r in results:
        if int(r["age"]) < kid_age_threshold and r["dominant_emotion"].lower() in [
            "fear",
            "disgust",
            "sad",
        ]:
            return True
        if r["dominant_gender"].lower() == "woman" and r[
            "dominant_emotion"
        ].lower() in ["fear", "disgust", "sad"]:
            return True
    return False
