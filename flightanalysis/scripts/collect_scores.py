from pathlib import Path
import argparse
import pandas as pd
from flightdata import fcj
from flightanalysis import enable_logging
from flightanalysis import ScheduleInfo
import plotly.express as px
from flightanalysis import AnalysisJson


def collect_scores(folder: Path):
    manscores = {}
    runinfo = {}
    for ajson in folder.rglob("*.ajson"):
        aj = AnalysisJson.model_validate_json(ajson.open().read())
        manscores[ajson.name] = aj.create_score_df(
            fcj.ScoreProperties(), group="total", version="All"
        )
        runinfo[ajson.name] = dict(
            bootTime=aj.bootTime,
            ajPath=str(ajson.absolute()),
            schedule=str(aj.schedule()),
        )

    scoredf = pd.concat(manscores, names=["file", "manoeuvre"])
    rundf = pd.DataFrame(runinfo).T

    k_factors = pd.concat(
        {k: ScheduleInfo.from_str(k).k_factors() for k in rundf.schedule.unique()},
        names=["schedule", "manoeuvre"],
    )

    totaldf = pd.DataFrame(
        {
            r[0]: scoredf.loc[r[0]].multiply(k_factors.loc[r[1].schedule], axis=0).sum(skipna=False)
            for r in rundf.iterrows()
        }
    ).sort_index()

    return pd.concat([rundf, totaldf.T], axis=1)


def plot_scores(scoredf):
    for version in scoredf.columns[3:]:
        px.scatter(
            scoredf, x="bootTime", y=version, color="schedule", hover_data="ajPath"
        ).show()


def collect_plot(folder: Path, outfile: Path = None):
    scoredf = collect_scores(folder)
    if outfile:
        scoredf.to_csv(outfile, index=False)
    plot_scores(scoredf)


def main():
    enable_logging()

    parser = argparse.ArgumentParser(
        description="Collect scores for all analysis jsons in a directory"
    )
    parser.add_argument(
        "-f", "--folder", default=".", help="Source directory, defaults to current"
    )
    parser.add_argument("-o", "--outfile", default="fcs_scores.csv", help="Output file")

    args = parser.parse_args()

    collect_plot(Path(args.folder), Path(args.outfile) if args.outfile else None)


if __name__ == "__main__":
   #collect_plot(Path("~/OneDrive/proj/logs/").expanduser())
    main()
