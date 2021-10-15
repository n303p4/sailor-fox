"""Check for health of images in reactions.json."""

import json

import requests


def main():
    """HEAD each URL and check its status. Flag URLs that return errors."""

    with open("reactions.json") as file_object:
        reactions = json.load(file_object)

    flagged_images = []

    for command_name, command_properties in reactions.items():
        images = command_properties.get("images")
        if not images:
            continue
        for image in images:
            print(f"{command_name} | {image} | ", end="")
            try:
                response = requests.head(image, timeout=5)
            except Exception:
                flagged_images.append(f"{command_name} | {image}")
                print("Timed out")
                continue
            print(response.status_code)
            if response.status_code >= 400:
                flagged_images.append(f"{command_name} | {image}")

    if flagged_images:
        print()
        print("== Images that need replacement ==")
        for image in flagged_images:
            print(image)


if __name__ == "__main__":
    main()
