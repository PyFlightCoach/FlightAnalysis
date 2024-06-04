from pathlib import Path
from loguru import logger
import sys
import argparse
import pandas as pd 
from flightanalysis import ScheduleAnalysis
from datetime import datetime
from flightanalysis.scripts.plot_scores import plot_logs

def main():
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    default_name = f'pfc_{datetime.now().strftime("%Y_%m_%d")}'

    parser = argparse.ArgumentParser(description='Collect scores for all analysis jsons in a directory')
    parser.add_argument('-f', '--folder', default=default_name, help=f'Source directory, defaults to {default_name}')
    parser.add_argument('-o', '--outfile', default=f'{default_name}_scores.csv', help='Output file')
    args = parser.parse_args()

    outdir = Path(args.folder)

    all_logs = [f for f in sorted(list(outdir.rglob('*analysis.json')))]

    odata = {}

    for log in all_logs:
        if log.stat().st_size == 0:
            logger.info(f'Empty file {log}')
            continue
        logger.info(f'Processing file {log}')
        sa = ScheduleAnalysis.from_fcscore(log)
        total, scores = sa.scores()
        if sa.sinfo.name.lower() not in odata:
            odata[sa.sinfo.name.lower()] = {}
        odata[sa.sinfo.name.lower()][log.stem] = dict(total=total, **scores)

    pd.options.display.float_format = '{:,.2f}'.format
    dfs = {}
    for sch, v in odata.items():
        dfs[sch] = pd.DataFrame.from_dict(v, orient='index')
        dfs[sch].index.name = 'source_file'

    for sch, res in dfs.items():
        logger.info(f'{sch}scores:\n{res}')

        res.to_csv(args.outfile.replace('_scores.csv', f'_{sch}_scores.csv'))

    plot_logs([args.outfile.replace('_scores.csv', f'_{sch}_scores.csv') for sch in dfs.keys()])


if __name__ == "__main__":
    main()