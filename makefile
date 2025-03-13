setup:
	python -m venv env-name \
    source env-name/bin/activate

install:
	pip install -r requirements.txt

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000