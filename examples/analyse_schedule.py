from flightanalysis.scripts.analyse_logs import create_ajson, run_analysis
from pathlib import Path
from flightdata.schemas.fcj import FCJ
from flightanalysis import enable_logging

enable_logging('INFO')

aj = create_ajson(FCJ.model_validate_json(Path("examples/data/manual_F3A_P23_22_05_31_00000350.json").open().read()))
aj = run_analysis(aj, False)

print(aj.get_scores(aj.all_versions()[-1]))