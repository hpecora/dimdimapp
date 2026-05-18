# Imagem base
FROM python:3.11-slim

# Metadados
LABEL maintainer="DimDimApp"
LABEL description="API RESTful - Instituição Financeira DimDim"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=8000 \
    DATABASE_URL=postgresql://dimdim:dimdim123@db-dimdim:5432/dimdimdb

# Diretório de trabalho
WORKDIR /dimdimapp

# Cria usuário não-root
RUN groupadd -r dimdimuser && useradd -r -g dimdimuser dimdimuser

# Copia e instala dependências ANTES do código (cache eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY app/ ./app/

# Ajusta permissões para o usuário não-root
RUN chown -R dimdimuser:dimdimuser /dimdimapp

# Troca para usuário não-root
USER dimdimuser

# Expõe a porta da aplicação
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
