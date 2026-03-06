# Mediastandard validation

The python scripts `mediastandard_validation.py` and `simple_mediastandard_validation.py` validate filenames with a _Mediastandard_ at [Kunstmuseum Basel](https://medienstandard.kumu.swiss/).

## Prerequisites

In order to run `mediastandard_validation.py`, install the requirements:

```
pip3 install -r requirements.txt 
```


## Use

Validate filenames:

```
python3 mediastandard_validation.py [OPTIONS] filename1 filename2 ... | directory


OPTIONS:

        -f|--fail-only  show only fails
        -h|--help       show help
        -j|--json=file  json file
        -p|--pattern    print regex pattern for mediastandard
        -v|--verbose    print file information

```

