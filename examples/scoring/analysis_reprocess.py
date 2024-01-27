from flightanalysis import ScheduleAnalysis, ScheduleInfo
from json import load


with open("/home/td6834/projects/logs/2024_01_05/manual_F3A_P25_24_01_05_00000174_analysis.json", 'r') as f:
    data = load(f)
sa: ScheduleAnalysis = ScheduleAnalysis.from_fcscore(data)



sa.dump_fcscore('00000174_analysis_python', ScheduleInfo('f3a', 'p25'), "/home/td6834/projects/logs/2024_01_05/00000174_analysis_python.json")




pass