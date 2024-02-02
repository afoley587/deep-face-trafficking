def is_possible_trafficking(results):
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
