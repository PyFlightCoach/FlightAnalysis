from pathlib import Path
import argparse
import pandas as pd
from flightanalysis.fcjson import FCJ
from flightanalysis import enable_logging, logger, ScheduleAnalysis
from flightanalysis.version import get_version
from datetime import date
from flightanalysis import ScheduleInfo
from dataclasses import dataclass
import re


@dataclass
class FCJScore:
    file: str
    name: str
    id: int
    created: date
    schedule: ScheduleInfo
    scores: pd.DataFrame

    @staticmethod
    def parse_fcj(file: str, fcj: FCJ):
        file = Path(file)

        return FCJScore(
            file=file,
            name=fcj.name,
            id=int(fcj.id),
            created=fcj.created,
            schedule=ScheduleInfo(*fcj.parameters.schedule).fcj_to_pfc(),
            scores=fcj.pfc_version_df()
            if len(fcj.fcs_scores) > 0
            else pd.DataFrame([]),
        )

    @staticmethod
    def parse_file(file: str):
        with open(file, "r") as f:
            fcj = FCJ.model_validate_json(f.read())
        return FCJScore.parse_fcj(file, fcj)

    def run_analysis(self):
        if get_version() not in self.version_totals():
            fcj = FCJ.model_validate_json(open(self.file, "r").read())

            sa = ScheduleAnalysis.from_fcj(fcj.model_dump()).run_all()
            data = sa.append_scores_to_fcj(fcj.model_dump(), self.file)
            return FCJScore.parse_fcj(self.file, FCJ.model_validate(data))
            # except Exception as e:
            #    logger.error(f'Error processing {self.file}: {e}')
            #    return self
        else:
            return self

    def __repr__(self):
        return f"FCJScore({self.file}, {self.created}, {self.schedule}, {list(self.scores.index.levels[0])})"

    def version_totals(self):
        if len(self.scores) == 0:
            return dict()
        else:
            return self.scores.groupby("version").kfac.sum().iloc[:, -1].to_dict()

    def summary(self):
        return dict(
            name=self.name,
            id=re.search(r"\d{8}", self.name)[0],
            file=self.file,
            created=self.created,
            schedule=self.schedule,
            **self.version_totals(),
        )


def collect_scores(files: list[str], run=False) -> pd.DataFrame:
    data = []
    for i, file in enumerate(files):
        logger.info(f"log {i} of {len(files)}: {file}")
        try:
            fcjscore = FCJScore.parse_file(file)
            if get_version() not in fcjscore.version_totals() and run:
                fcjscore = fcjscore.run_analysis()
            if len(fcjscore.scores) > 0:
                data.append(fcjscore.summary())
                logger.info(fcjscore.version_totals())
        except Exception as e:
            logger.error(f"Error processing {file}: {e}")

    return pd.DataFrame(data)


def main():
    enable_logging()

    parser = argparse.ArgumentParser(
        description="Collect scores for all analysis jsons in a directory"
    )
    parser.add_argument(
        "-f", "--folder", default=".", help="Source directory, defaults to current"
    )
    parser.add_argument("-o", "--outfile", default="fcs_scores.csv", help="Output file")
    parser.add_argument(
        "-r",
        "--run",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="run analysis for current version if it does not exist",
    )
    args = parser.parse_args()

    all_logs = sorted(list(Path(args.folder).rglob("*.json")))

    scoredf = collect_scores(all_logs, args.run)
    scoredf.to_csv(args.outfile, index=False)


if __name__ == "__main__":
    main()
