import pandas as pd
from pathlib import Path
import plotly.express as px
import re
from datetime import date
from plotly_templates.aiaa import aiaa_template
import argparse


def parse_name(file):
    data = re.findall(r"\w\d\d_\d\d_\d\d_\d\d+_\S+_",file)[0].split('_')
    return data[0], date(int(data[1]) + 2000, int(data[2]), int(data[3])) , data[4]

def plot_logs(files):
    
    data = pd.concat([pd.read_csv(file).assign(csv=file) for file in files], axis=0).reset_index(drop=True)
    index_df = pd.DataFrame(list(data.source_file.apply(parse_name)), columns=['schedule', 'date', 'name'])

    data = pd.concat([
        index_df, 
        data], axis=1)
    px.scatter(
        data, 
        x='date', 
        y='total',
        color = 'csv',
    ).update_layout(
        template=aiaa_template,
        yaxis=dict(range=(0,500), title='Total Score'), 
        xaxis=dict(title='date'), 
        title=f'Scores from a Set of {data.schedule.unique()} Flights',
        width=1000, height=600
    ).update_traces(
        marker=dict(size=10)
    ).show()

def main():
    parser = argparse.ArgumentParser(description='Collect scores for all analysis jsons in a directory')
    parser.add_argument('-f', '--files', default=list(Path('.').glob('*.csv')), help='Source files, defaults to None for all csvs in current directory')
    args = parser.parse_args()

    return plot_logs(args.files)


if __name__ == "__main__":
    main()