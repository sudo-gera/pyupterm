from hashlib import sha256
import os
import pathlib
from importlib.resources import files
from importlib.resources import as_file


def main() -> None:
    data_dir = files("pyupterm").joinpath("data")

    files 

    with as_file(data_dir) as data_path:

        for dirpath, dirnames, filenames in os.walk(str(data_path.resolve())):
            for filename in filenames:
                if filename.startswith('upterm'):
                    with open()

                    digest = sha256(blob.read_bytes()).hexdigest()

    for blob in sorted(data_dir.iterdir(), key=lambda path: path.name):
        if not blob.name.endswith(".bin"):
            continue

        print(f"{digest}  {blob.name}")


if __name__ == "__main__":
    main()