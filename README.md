conda create -n cloudberry python=3.10 pillow numpy
conda activate cloudberry
pip install poetry
poetry config virtualenvs.create false
poetry install
poetry run generate-proto
poetry run pytest