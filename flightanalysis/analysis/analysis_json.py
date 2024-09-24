from flightanalysis import ma, ScheduleInfo, ScheduleAnalysis
from flightdata import Origin, State





def create_analysis_json(
    origin: Origin, sbin: str, sfcj: str, st: State, sa: ScheduleAnalysis
):
    pass


# readonly box: Origin,
# readonly isComp: boolean,
# readonly sourceBin: string,
# readonly sourceFCJ: string,
# readonly mans: MAExport[],
# readonly states: States


# readonly name: string,
# readonly id: number,
# readonly sinfo: ScheduleInfo,
# readonly start: number,
# readonly stop: number,
#       readonly k: number,
# readonly history: Record<string, FCJManResult> = {},
