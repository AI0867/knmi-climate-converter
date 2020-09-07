# knmi-climate-converter

Conversion script for KNMI historical hourly measurements to projected climate-changed values. This provides a somewhat crude projection of hourly temperatures in the future.

### Method

Using the difference between KNMI's own daily climate projections and the historical daily values those are based on, hourly temperatures from within this range are adjusted.

### Purpose

This script was written to enable Vabi Elements to use KNMI's climate projections. Vabi Elements requires a file with hourly temperature values.

### Configuration

All configurable values are located at the top of the script. This includes input and output filenames.

### Files and licenses

The [KNMI14____ref_tg___19810101-20101231_v3.2.txt](KNMI14____ref_tg___19810101-20101231_v3.2.txt), [KNMI14_WH_2050_tg___19810101-20101231_v3.2.txt](KNMI14_WH_2050_tg___19810101-20101231_v3.2.txt) and [uurgeg_344_2001-2010.txt](uurgeg_344_2001-2010.txt) files are owned by the [KNMI][knmi] and were retrieved from [their website][knmi-web]. They are included here because some of them are diffcult to find.

The [uurgeg_344_2001-2010_WH_2050.txt](uurgeg_344_2001-2010_WH_2050.txt) file is the output of the conversion script and is included here for convenience. Being a product of the previous three files, it falls under the same license.

The [convert.py](convert.py) script and this [README.md](README.md) are released under the MIT license, included in [LICENSE](LICENSE).

[knmi]: https://github.com/KNMI "KNMI GitHub page"
[knmi-web]: http://www.klimaatscenarios.nl/ "KNMI Klimaatscenarios"
