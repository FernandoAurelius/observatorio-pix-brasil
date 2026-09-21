FROM python:3.13-slim
WORKDIR /aplicacao
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/aplicacao/pacotes:/aplicacao/aplicacoes/api
COPY requirements-producao.txt ./
RUN pip install --no-cache-dir -r requirements-producao.txt && useradd --create-home observatorio
COPY pacotes ./pacotes
COPY aplicacoes/api/observatorio_api ./aplicacoes/api/observatorio_api
USER observatorio
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/saude',timeout=4)"
CMD ["uvicorn","observatorio_api.principal:aplicacao","--host","0.0.0.0","--port","8000","--workers","1"]
