from pathlib import Path
from flightanalysis import ScheduleAnalysis
from flightdata import NumpyEncoder
from json import load
from loguru import logger
from json import dump, dumps
import sys
import argparse
from datetime import datetime

def main():

    logger.enable("flightanalysis")
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    default_name = f'pfc_{datetime.now().strftime("%Y_%m_%d")}'

    parser = argparse.ArgumentParser(description='Analyse all fc jsons in the current directory')
    parser.add_argument('-o', '--outdir', default=default_name, help=f'Output directory, defaults to {default_name}')
    parser.add_argument('-f', '--folder', default='', help='input directory, defaults to current directory')
    parser.add_argument('-r', '--recursive', default=False, action=argparse.BooleanOptionalAction, help='include subdirectories in search, default is False')
    parser.add_argument('-s', '--search', default='*.json', help='json Search string, defaults to *F3A*.json')
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    indir = Path(args.folder)

    search_result = indir.rglob(args.search) if args.recursive else indir.glob(args.search)

    all_logs = [f for f in sorted(list(search_result)) if ('analysis.json' not in f.name)]

    for i, file in enumerate(all_logs):
        outfile = outdir / f'{file.stem}_analysis.json'
        if outfile.exists(): 
            continue
        try:
            logger.info(f'Processing file {i} of {len(all_logs)} - {file}')
            data = load(open(file, 'r'))
            
            if 'analysis.json' not in file.name:
                sa = ScheduleAnalysis.from_fcj(data)
            else:
                sa = ScheduleAnalysis.from_fcscore(data)
            logger.info(sa.sinfo)
            sa = sa.run_all()

            with open(outdir / f'{file.stem}_analysis.json', 'w') as f:
                dump(sa.to_fcscore(file.stem), f, indent=4, cls=NumpyEncoder)
            logger.info(f'scores:\n{dumps(sa.scores(), indent=2)}')
        except Exception as e:
            logger.error(f'Error processing {file}: {e}')


if __name__ == '__main__':
    main()