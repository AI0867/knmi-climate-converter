#!/usr/bin/env python3

# Copyright 2020 Alexander van Gessel <ai0867@gmail.com>
#
# Conversion script for KNMI historical hourly measurements to projected
#  climate-changed values.
# Projection is done based on the difference KNMI's own daily climate
#  projections and the historical daily values those are based on.
# Only temperatures are converted.
# This script was written to enable Vabi Elements to use KNMI's
#  climate projections.

UUR_IN="uurgeg_344_2001-2010.txt"
DAG_ORIG="KNMI14____ref_tg___19810101-20101231_v3.2.txt"
DAG_TRANS="KNMI14____2030_tg___19810101-20101231_v3.2.txt"
UUR_OUT="uurgeg_344_2001-2010____2030.txt"
STATION="344"

class Comparer:
    def __init__(self, original, transformed, station):
        self._data = {}
        self._load_data(original, transformed, station)
    def get_diff(self, date, _hour, *args):
        return self._data[date]
    def _load_data(self, original, transformed, station):
        """Doing everything on startup. File sizes are acceptable for this"""
        fd_orig = open(original, "r")
        fd_trans = open(transformed, "r")
        col_orig = self._scroll_and_find_col(fd_orig, station)
        col_trans = self._scroll_and_find_col(fd_trans, station)
        data_lineno = 0
        while True:
            orig = fd_orig.readline()
            trans = fd_trans.readline()
            if not orig.strip() and not trans.strip():
                break
            if not orig.strip() or not trans.strip():
                raise ValueError("Files did not match.\nOrig:\t{}\nTrans:\t{}".format(orig, trans))
            split_orig = orig.split()
            split_trans = trans.split()
            date = split_orig[0]
            if date != split_trans[0]:
                raise ValueError("Data line {} date mismatch {} vs {}".format(data_lineno, date, split_trans[0]))
            self._data[date] = float(split_trans[col_trans]) - float(split_orig[col_orig])
            data_lineno += 1
    def _scroll_and_find_col(self, fd, station):
        """Move cursor to first data row, while finding which column contains our data"""
        METADATA="00000000"
        # First lines are comments
        while (line := fd.readline()).startswith("#"):
            pass
        # Following lines are metadata (date 00000000), identifying station number, ?, ?, lat, long
        # Current line is station identifier
        stations = line.split()
        if stations[0] != METADATA:
            raise ValueError("First non-comment line does not appear to be a metadata line: {}".format(line))
        try:
            column = stations.index(station)
        except ValueError as e:
            raise ValueError("Station {} not found in stations {}".format(station, stations[1:]), e)
        # Eat next 4 metadata lines
        for lineno in range(1, 5):
            if (line := fd.readline()).split()[0] != METADATA:
                raise ValueError("Line #{} of what should be metadata appears to not be metadata: {}".format(lineno, line))
        return column

class Transformer:
    def __init__(self, comparer, uur_in, uur_out, station):
        self._comparer = comparer
        self._fd_in = open(uur_in, "r")
        self._fd_out = open(uur_out, "w", newline='\r\n')
        self._station = station
    def transform(self):
        STATION="STN"
        DATE="YYYYMMDD"
        HOUR="HH"
        TEMP="T"
        T10N="T10N"
        # File starts with some commentary not starting with comment markers
        while not (line := self._fd_in.readline()).startswith("#"):
            self._fd_out.write(line)
        # Current line is a commented header line
        self._fd_out.write(line)
        headers = [header.strip() for header in line[1:].split(",")]
        try:
            col_station = headers.index(STATION)
            col_date = headers.index(DATE)
            col_hour = headers.index(HOUR)
            col_temp = headers.index(TEMP)
            col_t10n = headers.index(T10N)
        except ValueError as e:
            raise ValueError("Required column not found in headers: {}".format(headers), e)
        # Now everything is just data to transform
        lines_transformed = 0
        while (line := self._fd_in.readline()):
            if not line.strip():
                self._fd_out.write(line)
                continue
            values = [val for val in line.split(",")]
            # Types of values: ints, int-like strings (such as dates) and int-like flags (0 or 1). Some values may be empty (empty string)
            station = values[col_station].strip()
            date = values[col_date]
            hour = values[col_hour]
            temp_in = int(values[col_temp].strip()) # Temp in deci-degrees Celsius
            t10n_in_raw = values[col_t10n] # May be empty
            t10n_in = int(t10n_in_raw.strip()) if t10n_in_raw.strip() else None # T10n in deci-degrees Celsius
            if station != self._station:
                raise ValueError("Incorrect station ID. Expected {} but found {} during day {}".format(self._station, station, date))
            temp_diff = 10 * self._comparer.get_diff(date, hour)
            out_vals = values[:]
            temp_out = int(temp_in + temp_diff) # The difference may be floatified
            # Formatting: every column is right-justified to 5 characters, which is sufficient for every column except date
            out_vals[col_temp] = str(temp_out).rjust(5)
            if t10n_in is not None:
                t10n_out = int(t10n_in + temp_diff)
                out_vals[col_t10n] = str(t10n_out).rjust(5)
            line_out = ",".join(out_vals)
            self._fd_out.write(line_out)
            lines_transformed += 1
        return lines_transformed

if __name__ == "__main__":
    print("Comparing\n\t{}\nwith\n\t{}\nto transform\n\t{}\nto\n\t{}".format(DAG_ORIG, DAG_TRANS, UUR_IN, UUR_OUT))
    comp = Comparer(DAG_ORIG, DAG_TRANS, STATION)
    transformer = Transformer(comp, UUR_IN, UUR_OUT, STATION)
    lines = transformer.transform()
    print("Transformed {} lines".format(lines))
