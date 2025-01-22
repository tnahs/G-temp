import argparse
import textwrap
from importlib import metadata
from pathlib import Path


APP_NAME = "gtemp"
APP_VERSION = metadata.version(APP_NAME)

GCODE_SUFFIX = ".gcode"
GCODE_TEMPLATE_SUFFIX = ".gtemplate"

NOZZLE_TEMP_CGODE_COMMAND = "M104"
NOZZLE_TEMP_TEMPLATE_TEXT = "##NOZZLETEMP##"

NOZZLE_TEMP_PRESETS = {
    "PLA": [
        230,
        225,
        220,
        215,
        210,
        205,
        200,
        195,
        190,
    ],
    "PETG": [
        260,
        255,
        250,
        245,
        240,
        235,
        230,
        225,
        220,
        215,
        210,
    ],
    "PETG-CF": [
        260,
        255,
        250,
        245,
        240,
        235,
        230,
        225,
        220,
        215,
        210,
    ],
}


def validate_gcode_templates(gcode_templates: list[Path]) -> bool:
    template_filename_errors = validate_gcode_template_filenames(gcode_templates)
    template_content_errors = validate_gcode_template_contents(gcode_templates)

    if template_filename_errors or template_content_errors:
        if template_filename_errors:
            print("\nError: the following templates have invalid file names:")
            for template_filename in template_filename_errors:
                print(f"  {template_filename}")

        if template_content_errors:
            print(
                f"Error: the following templates are missing nozzle temperature template "
                f"text '{NOZZLE_TEMP_CGODE_COMMAND} {NOZZLE_TEMP_TEMPLATE_TEXT}':"
            )
            for template_filename in template_content_errors:
                print(f"  {template_filename}")

        return False

    return True


def validate_gcode_template_filenames(gcode_templates: list[Path]) -> list[str]:
    return [
        gcode_template.name
        for gcode_template in gcode_templates
        if f"{NOZZLE_TEMP_TEMPLATE_TEXT}" not in gcode_template.name
    ]


def validate_gcode_template_contents(gcode_templates: list[Path]) -> list[str]:
    return [
        gcode_template.name
        for gcode_template in gcode_templates
        if f"{NOZZLE_TEMP_CGODE_COMMAND} {NOZZLE_TEMP_TEMPLATE_TEXT}"
        not in gcode_template.read_text()
    ]


def render_gcode_templates(
    gcode_templates: list[Path],
    nozzle_temps: list[int],
    output: Path,
) -> None:
    print(f"\nRendering {len(gcode_templates) * len(nozzle_temps)} G-code files:")

    for gcode_template in gcode_templates:
        original_content = gcode_template.read_text()

        for nozzle_temp in nozzle_temps:
            modified_content = original_content.replace(
                NOZZLE_TEMP_TEMPLATE_TEXT, f"S{nozzle_temp}"
            )

            modified_filename = gcode_template.stem.replace(
                NOZZLE_TEMP_TEMPLATE_TEXT, f"{nozzle_temp}C"
            )

            modified_file = output / modified_filename
            modified_file = modified_file.with_suffix(GCODE_SUFFIX)

            print(f"  {nozzle_temp}C for {modified_file.name}")

            modified_file.write_text(modified_content)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        add_help=False,
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent(
            f"""
            Generate an array of G-code files with different nozzle temperatures.

            \033[4mUsage:\033[0m
              {APP_NAME} [OPTIONS] [ARGS]

            \033[4mRequired Arguments:\033[0m
              -t, --templates PATH           Path containing G-code templates: '[name]{GCODE_TEMPLATE_SUFFIX}'
              -o, --output PATH              G-code file output directory
              -p, --temps-preset MATERIAL    Select a preset list of nozzle temperatures...
              -c, --temps-custom [TEMP ...]  ...or provide a custom list

            \033[4mOptional Arguments:\033[0m
              -h, --help     Show help
              -v, --version  Print version

            \033[4mDocumentaion:\033[0m

              A G-code template is an ASCII G-code file that contains three things:

                1. Its filename ends in '{GCODE_TEMPLATE_SUFFIX}'. At render time, this will be replaced
                   with '{GCODE_SUFFIX}'.

                2. Its filename contains the template text '{NOZZLE_TEMP_TEMPLATE_TEXT}'. At render time,
                   this will be replaced with the temperature followed by a 'C'. For example:

                     [prefix]_{NOZZLE_TEMP_TEMPLATE_TEXT}_[suffx]{GCODE_TEMPLATE_SUFFIX}'
                     [prefix]_230C_[suffx]{GCODE_SUFFIX}'

                3. The file contains the nozzle temperature change G-code command '{NOZZLE_TEMP_CGODE_COMMAND}'
                   followed by the template text '{NOZZLE_TEMP_TEMPLATE_TEXT}'. This will be replaced with
                   the temperature prefixed with an 'S'. For example:

                     {NOZZLE_TEMP_CGODE_COMMAND} {NOZZLE_TEMP_TEMPLATE_TEXT} ; set temperature
                     {NOZZLE_TEMP_CGODE_COMMAND} S230 ; set temperature
        """.rstrip()
        ),
    )

    parser.add_argument(
        "-t",
        "--templates",
        type=Path,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help=argparse.SUPPRESS,
    )

    nozzle_temps = parser.add_mutually_exclusive_group(required=True)
    nozzle_temps.add_argument(
        "-p",
        "--temps-preset",
        choices=NOZZLE_TEMP_PRESETS.keys(),
        type=str,
        help=argparse.SUPPRESS,
    )
    nozzle_temps.add_argument(
        "-c",
        "--temps-custom",
        nargs="+",
        type=int,
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{APP_NAME} v{APP_VERSION}",
        help=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    templates: Path = args.templates.resolve()
    output: Path = args.output.resolve()

    if not templates.is_dir() or not templates.exists():
        parser.error(f"the 'templates' path is not a valid directory: {templates}")

    if not output.is_dir() or not output.exists():
        parser.error(f"the 'output' path is not a valid directory: {output}")

    nozzle_temps = (
        args.nozzle_temps_custom  # noqa: FURB110
        if args.nozzle_temps_custom
        else NOZZLE_TEMP_PRESETS.get(args.nozzle_temps_preset)
    )

    if nozzle_temps is None:
        raise ValueError(f"invalid preset selected: {args.nozzle_temps_preset}")

    gcode_templates = list(templates.glob(f"*{GCODE_TEMPLATE_SUFFIX}"))

    print(f"Applying nozzle temps {nozzle_temps} to {len(gcode_templates)} templates:")
    for path in gcode_templates:
        print(f"  {path.parent.name}/{path.name}")

    if input("\nConfirm? [Y/n]: ").lower() not in {"", " ", "yes", "y"}:
        print("Aborting export!")
        return 1

    if not validate_gcode_templates(gcode_templates):
        return 1

    render_gcode_templates(gcode_templates, nozzle_temps, output)

    return 0
