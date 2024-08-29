import pandas as pd
from pathlib import Path
import plotly.express as px
import re
from datetime import date
import argparse
import numpy as np
from packaging.version import Version


def plot_score_csv(file: Path):
    scoredf = pd.read_csv(file)
    scoredf["created"] = pd.to_datetime(scoredf.created)
    scoredf.columns = list(scoredf.columns[:5]) + [
        v[1:] if v.startswith("v") else v for v in scoredf.columns[5:]
    ]
    versions = sorted(scoredf.columns[5:])

    px.scatter(
        scoredf, x=versions[-1], y=versions, symbol="schedule", hover_data="file"
    ).show()

    df = pd.melt(
        scoredf,
        id_vars=["id", "created", "schedule", "file"],
        value_vars=scoredf.columns[5:],
        var_name="version",
        value_name="score",
    )

    px.scatter(
        df,
        x="created",
        y="score",
        color="version",
        hover_data="file",
        symbol="schedule",
    ).show()

    px.scatter(
        scoredf, x="created", y=versions[-1], color="schedule", hover_data="file"
    ).show()


def main():
    parser = argparse.ArgumentParser(description="Plot scores from a csv file")

    parser.add_argument("-f", "--file", default="fcs_scores.csv", help="Score file")
    args = parser.parse_args()

    plot_score_csv(Path(args.file))


if __name__ == "__main__":
    # main()
    plot_score_csv(Path("~/projects/logs/fcs_scores.csv").expanduser())
