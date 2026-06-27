import argparse
from pathlib import Path
import re

FRAME_PATTERN = re.compile(r"^(?P<prefix>.*?)(?P<number>\d+)(?P<suffix>\.[^.]+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename frame files in a directory with sequential indices starting from 1000."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="training_frames_output_near",
        help="Directory containing the files to rename.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1000,
        help="Starting index for renamed files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the rename mapping without making changes.",
    )
    return parser.parse_args()


def gather_files(directory: Path) -> list[Path]:
    files = [path for path in directory.iterdir() if path.is_file()]
    ordered = []

    for path in files:
        match = FRAME_PATTERN.match(path.name)
        if match:
            ordered.append((int(match.group("number")), path))

    ordered.sort(key=lambda item: item[0])
    return [path for _, path in ordered]


def build_target_names(files: list[Path], start_index: int) -> dict[Path, Path]:
    target_map: dict[Path, Path] = {}
    width = max(4, len(str(start_index + len(files) - 1)))

    for offset, path in enumerate(files):
        match = FRAME_PATTERN.match(path.name)
        if not match:
            continue

        prefix = match.group("prefix")
        suffix = match.group("suffix")
        target_name = f"{prefix}{start_index + offset:0{width}d}{suffix}"
        target_map[path] = path.with_name(target_name)

    return target_map


def rename_files(target_map: dict[Path, Path], dry_run: bool = False) -> None:
    if not target_map:
        print("No matching frame files found.")
        return

    for src, dst in target_map.items():
        print(f"{src.name} -> {dst.name}")

    if dry_run:
        print("Dry run complete. No files were renamed.")
        return

    temp_map = {}
    for src in target_map:
        temp_path = src.with_name(src.name + ".rename_tmp")
        temp_map[src] = temp_path

    for src, temp_path in temp_map.items():
        src.rename(temp_path)

    for src, temp_path in temp_map.items():
        dst = target_map[src]
        if dst.exists():
            raise FileExistsError(f"Target file already exists: {dst}")
        temp_path.rename(dst)

    print("Rename completed.")


def main() -> None:
    args = parse_args()
    directory = Path(args.directory)

    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = gather_files(directory)
    target_map = build_target_names(files, args.start)
    rename_files(target_map, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
