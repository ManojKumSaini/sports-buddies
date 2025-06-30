import os
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from functions import get_user_number_from_config, data_from_data_sink
user = get_user_number_from_config()

sources = data_from_data_sink(f"SELECT data_source FROM fact_raw_data WHERE user_number = {user};")
sources = sources["data_source"].tolist()

def execute_notebook(notebook_path):
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='myenv')
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
    print(f"✅ Notebook ausgeführt: {notebook_path}")

if "health" in sources:
    print("run health")
    execute_notebook("03_health_aggregation.ipynb")

if "strava" in sources:
    print("run strava")
    execute_notebook("04_strava_aggregation.ipynb")

if "linkedin" in sources:
    print("run linkedin")
    execute_notebook("05_linkedin_aggregation.ipynb")

if "steam" in sources:
    print("run steam")
    execute_notebook("06_steam_aggregation.ipynb")

if "github" in sources:
    print("run github")
    execute_notebook("07_github_aggregation.ipynb")

if "spotify" in sources:
    print("run spotify")
    execute_notebook("08_spotify_aggregation.ipynb")
    
print("done!")
    