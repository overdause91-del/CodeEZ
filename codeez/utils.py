import sys
import shutil


def terminal_width() -> int:
    return shutil.get_terminal_size((80, 20)).columns


def print_separator(char="="):
    print(char * terminal_width())


def print_header(text: str):
    print_separator()
    print(f"  {text}")
    print_separator()


def print_error(msg: str):
    print(f" {msg}", file=sys.stderr)


def print_success(msg: str):
    print(f" {msg}")


def print_info(msg: str):
    print(f" * {msg}")
