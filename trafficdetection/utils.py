import argparse
import os

import cv2
from loguru import logger

from detectors.bufferedvideoreader import BufferedVideoReader
from detectors.imagereader import ImageReader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--video-device", type=int, required=False)
    parser.add_argument("-f", "--video-file", type=str, required=False)
    parser.add_argument("-i", "--images-directory", type=str, required=False)
    parser.add_argument(
        "-r", "--save-results", action="store_true", required=False, default=True
    )
    parser.add_argument(
        "-s", "--show-results", action="store_true", required=False, default=True
    )
    return parser.parse_args()


def analyze_video(device=0, criterias=[], show=True, save=True):
    # Create a video capture instance.
    # VideoCapture(0) corresponds to your computers
    # webcam
    cap = BufferedVideoReader(device)

    # Lets grab the frames-per-second (FPS) of the
    # webcam so our output has a similar FPS.
    # Lets also grab the height and width so our
    # output is the same size as the webcam
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    cap.set_analyze_every(int(fps) * 1)  # Every XX seconds

    # Now lets create the video writer. We will
    # write our processed frames to this object
    # to create the processed video.
    out = cv2.VideoWriter(
        "outpy.avi",
        cv2.VideoWriter_fourcc("M", "J", "P", "G"),
        fps,
        (frame_width, frame_height),
    )

    cv2.namedWindow("Video")

    while True:
        # Capture frame-by-frame
        frame = cap.read()

        if frame is None:
            break

        frame, res = cap.process(frame)

        for criteria in criterias:
            if criteria(res):
                # Eventually do some processing here
                label = criteria.__name__
                logger.info(f"Found Possible Criteria Match - {label}")
                (diff_x, diff_y), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                h, w, _ = frame.shape
                cv2.rectangle(
                    frame,
                    ((w - diff_x) // 2, h - 2 * diff_y),
                    ((w + diff_x) // 2, h),
                    (255, 255, 255),
                    -1,
                )
                cv2.putText(
                    frame,
                    label,
                    ((w - diff_x) // 2, h - diff_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 0, 0),
                    2,
                )

        if save:
            out.write(frame)

        if show:
            # Show the frame
            do_break = show_frame_and_wait(frame, named_window="Video", wait=1)
            if do_break:
                break


def analyze_image(filename, criterias=[], show=True, save=True):
    ir = ImageReader()
    frame = ir.read(filename)
    frame, res = ir.process(frame)

    for criteria in criterias:
        if criteria(res):
            # Eventually do some processing here
            label = criteria.__name__
            logger.info(f"Found Possible Criteria Match - {label}")
            (diff_x, diff_y), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
            h, w, _ = frame.shape
            cv2.rectangle(
                frame,
                ((w - diff_x) // 2, h - 2 * diff_y),
                ((w + diff_x) // 2, h),
                (255, 255, 255),
                -1,
            )
            cv2.putText(
                frame,
                label,
                ((w - diff_x) // 2, h - diff_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                1,
            )

    if save:
        save_to = filename.split(".")
        save_to.insert(-1, "processed")  # put "processed" right before extension
        save_to_str = ".".join(save_to)
        logger.info(f"saving to {save_to_str}")
        cv2.imwrite(f"{save_to_str}", frame)

    if show:
        show_frame_and_wait(frame)


def show_frame_and_wait(frame, named_window="window", wait=5000):
    cv2.imshow(named_window, frame)
    if cv2.waitKey(wait) & 0xFF == ord("q"):
        return True
