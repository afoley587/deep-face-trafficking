import os
import utils
from loguru import logger
from criteria.trafficking import is_possible_trafficking


def main():
    args = utils.parse_args()

    if args.rabbit is not None:
        # Streams From A camera
        utils.analyze_rabbit(
            params=args.rabbit,
            criterias=[is_possible_trafficking],
            show=args.show_results,
            save=args.save_results,
        )
    if args.video_device is not None:
        # Streams From A camera
        utils.analyze_video(
            device=args.video_device,
            criterias=[is_possible_trafficking],
            show=args.show_results,
            save=args.save_results,
        )
    if args.video_file is not None:
        # Streams From A camera
        utils.analyze_video(
            device=args.video_file,
            criterias=[is_possible_trafficking],
            show=args.show_results,
            save=args.save_results,
        )

    if args.images_directory is not None:
        if not os.path.exists(args.images_directory):
            logger.error(f"{args.images_directory} Does Not Exist")
            raise FileNotFoundError

        # Spot check images
        for root, subdir, files in os.walk(args.images_directory):
            for file in files:
                path = os.path.join(root, file)
                utils.analyze_image(
                    path,
                    criterias=[is_possible_trafficking],
                    show=args.show_results,
                    save=args.save_results,
                )


if __name__ == "__main__":
    main()
