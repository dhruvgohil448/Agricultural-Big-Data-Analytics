"""
tests/test_mapreduce.py
Unit tests verifying MapReduce mapper and reducer logic against small fixtures.
"""

import subprocess
import pytest

MOCK_CROP_INPUT = """State_Name,District_Name,Crop_Year,Season,Crop,Area,Production
Punjab,Ludhiana,2010,Rabi,Wheat,100.0,420.0
Punjab,Patiala,2010,Rabi,Wheat,200.0,860.0
Punjab,Ludhiana,2010,Kharif,Rice,150.0,600.0
Kerala,Kollam,2010,Whole Year,Coconut,50.0,200000.0
"""

MOCK_RAIN_INPUT = """SUBDIVISION,YEAR,JAN,FEB,MAR,APR,MAY,JUN,JUL,AUG,SEP,OCT,NOV,DEC,ANNUAL,Jan-Feb,Mar-May,Jun-Sep,Oct-Dec
PUNJAB,1990,10,20,15,5,10,50,150,120,60,10,5,5,460,30,30,380,20
PUNJAB,1991,15,25,20,10,15,60,160,130,70,15,10,10,500,40,45,420,35
"""

def test_crop_mapreduce_pipeline():
    # 1. Run Mapper
    mapper_proc = subprocess.Popen(
        ["./.venv/bin/python", "src/mapreduce/crop_mapper.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    mapper_out, _ = mapper_proc.communicate(input=MOCK_CROP_INPUT)
    assert mapper_proc.returncode == 0
    assert "Punjab##Wheat##2010\t100.00\t420.00" in mapper_out
    assert "Punjab##Wheat##2010\t200.00\t860.00" in mapper_out

    # 2. Sort and Run Reducer
    sorted_lines = "\n".join(sorted(mapper_out.strip().split("\n"))) + "\n"
    reducer_proc = subprocess.Popen(
        ["./.venv/bin/python", "src/mapreduce/crop_reducer.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    reducer_out, _ = reducer_proc.communicate(input=sorted_lines)
    assert reducer_proc.returncode == 0

    # Expected: Punjab, Wheat, 2010 -> Area: 300.00, Prod: 1280.00, Mean Yield: 1280/300 = 4.2667
    assert "Punjab\tWheat\t2010\t300.00\t1280.00\t4.2667\t2" in reducer_out
    # Expected: Punjab, Rice, 2010 -> Area: 150.00, Prod: 600.00, Mean Yield: 4.0000
    assert "Punjab\tRice\t2010\t150.00\t600.00\t4.0000\t1" in reducer_out

def test_rainfall_mapreduce_pipeline():
    mapper_proc = subprocess.Popen(
        ["./.venv/bin/python", "src/mapreduce/rainfall_mapper.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    mapper_out, _ = mapper_proc.communicate(input=MOCK_RAIN_INPUT)
    assert mapper_proc.returncode == 0
    assert "PUNJAB##1990s\t460.00\t380.00\t1" in mapper_out
    assert "PUNJAB##1990s\t500.00\t420.00\t1" in mapper_out

    sorted_lines = "\n".join(sorted(mapper_out.strip().split("\n"))) + "\n"
    reducer_proc = subprocess.Popen(
        ["./.venv/bin/python", "src/mapreduce/rainfall_reducer.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    reducer_out, _ = reducer_proc.communicate(input=sorted_lines)
    assert reducer_proc.returncode == 0

    # Average annual: (460 + 500) / 2 = 480.00
    # Average monsoon: (380 + 420) / 2 = 400.00
    assert "PUNJAB\t1990s\t480.00\t400.00\t2" in reducer_out
