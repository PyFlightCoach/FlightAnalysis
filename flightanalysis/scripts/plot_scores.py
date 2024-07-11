import pandas as pd
from pathlib import Path
import plotly.express as px
import re
from datetime import date
import argparse


def main():
    parser = argparse.ArgumentParser(description='Plot scores from a csv file')

    parser.add_argument('-f', '--file', default='fcs_scores.csv', help='Score file')
    args = parser.parse_args()

    scoredf = pd.read_csv(args.file)

    for col in scoredf.columns[3:]:
        px.scatter(scoredf, x='created', y=col, color='schedule', hover_data='file').show()


if __name__ == "__main__":
    main()