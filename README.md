# gtemp

Generate an array of G-code files with different nozzle temperatures.

```plaintext
Usage:
  gtemp [OPTIONS] [ARGS]

Required Arguments:
  -t, --templates PATH           Path containing G-code templates: '[name].gtemplate'
  -o, --output PATH              G-code file output directory
  -p, --temps-preset MATERIAL    Select a preset list of nozzle temperatures...
  -c, --temps-custom [TEMP ...]  ...or provide a custom list

Optional Arguments:
  -h, --help     Show help
  -v, --version  Print version

Documentaion:

  A G-code template is an ASCII G-code file that contains three things:

    1. Its filename ends in '.gtemplate'. At render time, this will be replaced
       with '.gcode'.

    2. Its filename contains the template text '##NOZZLETEMP##'. At render time,
       this will be replaced with the temperature followed by a 'C'. For example:

         [prefix]_##NOZZLETEMP##_[suffx].gtemplate'
         [prefix]_230C_[suffx].gcode'

    3. The file contains the nozzle temperature change G-code command 'M104'
       followed by the template text '##NOZZLETEMP##'. This will be replaced with
       the temperature prefixed with an 'S'. For example:

         M104 ##NOZZLETEMP## ; set temperature
         M104 S230 ; set temperature
```

## Installation

The recommended method for installation requires [`uv`][uv]. This allows us to easily install
`gtemp` into its own virtual environment with the correct version of python and add it to `PATH`.

1. Install `uv`.

   See the [uv docs][uv] for the latest instructions.

2. Clone this repo.

   ```shell
   $ git clone https://github.com/tnahs/gtemp
   $ cd gtemp
   ```

3. Install using `uv`.

   ```shell
   $ uv tool install . --force --no-cache
   ```

4. Check the installation.

   ```shell
    $ gtemp --version
   ```

5. That's it! Run `--help` to see available options and documentation.

   ```shell
   $ gtemp --help
   ```

## Example

Using the following files:

```plaintext
model
├── gcode
│   ├── PETG
│   └── PLA
└── gtemplates
    ├── PETG
    │   └── model_PETG-Generic_##NOZZLETEMP##_43m.gtemplate
    └── PLA
        └── model_PLA-Generic_##NOZZLETEMP##_41m.gtemplate
```

We render the PETG template with the following command:

```shell
gtemp                                \
  --templates-path ./gtemplates/PETG \
  --nozzle-temps-preset PETG         \
  --output ./gcode/PETG
```

And then the PLA template with the following command:

```shell
gtemp                               \
  --templates-path ./gtemplates/PLA \
  --nozzle-temps-preset PLA         \
  --output ./gcode/PLA
```

Results in the following files:

```plaintext
model
├── gcode
│   ├── PETG
│   │   ├── model_PETG-Generic_210C_43m.gcode
│   │   ├── model_PETG-Generic_215C_43m.gcode
│   │   ├── model_PETG-Generic_220C_43m.gcode
│   │   ├── model_PETG-Generic_225C_43m.gcode
│   │   ├── model_PETG-Generic_230C_43m.gcode
│   │   ├── model_PETG-Generic_235C_43m.gcode
│   │   ├── model_PETG-Generic_240C_43m.gcode
│   │   ├── model_PETG-Generic_245C_43m.gcode
│   │   ├── model_PETG-Generic_250C_43m.gcode
│   │   ├── model_PETG-Generic_255C_43m.gcode
│   │   └── model_PETG-Generic_260C_43m.gcode
│   └── PLA
│       ├── model_PLA-Generic_190C_41m.gcode
│       ├── model_PLA-Generic_195C_41m.gcode
│       ├── model_PLA-Generic_200C_41m.gcode
│       ├── model_PLA-Generic_205C_41m.gcode
│       ├── model_PLA-Generic_210C_41m.gcode
│       ├── model_PLA-Generic_215C_41m.gcode
│       ├── model_PLA-Generic_220C_41m.gcode
│       ├── model_PLA-Generic_225C_41m.gcode
│       └── model_PLA-Generic_230C_41m.gcode
└── gtemplates
    └── ...
```

[uv]: https://docs.astral.sh/uv/
