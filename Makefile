.PHONY: instalar api web formatar lint-python testar validar evidencias executar
instalar:
	python -m pip install -r requirements.txt
	python -m pip install -e . --no-deps
	npm install
api:
	uvicorn observatorio_api.principal:aplicacao --reload --host 127.0.0.1 --port 8000
web:
	npm run dev
formatar:
	ruff check --fix .
	ruff format .
lint-python:
	ruff check .
	ruff format --check .
testar:
	python -m pytest --cov --cov-report=term-missing
validar:
	python scripts/validar_nucleo.py
evidencias:
	python scripts/gerar_evidencias.py --inicio 202501 --fim 202512
executar:
	docker compose up --build
