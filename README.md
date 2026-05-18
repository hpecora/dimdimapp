# DimDimApp — CP3 DevOps Tools & Cloud Computing | FIAP

API RESTful para a Instituição Financeira DimDim, containerizada com Docker e executada em nuvem (Azure).

---

## 🗂️ Estrutura do Projeto

```
dimdimapp/
├── app/
│   ├── __init__.py
│   └── main.py          # API FastAPI (CRUD completo)
├── Dockerfile           # Imagem da aplicação
├── requirements.txt
└── README.md
```

---

## 🐳 Arquitetura Docker

| Container | Imagem | Papel |
|---|---|---|
| `app-dimdim-556612` | Custom (Dockerfile) | API FastAPI Python |
| `db-dimdim-556612` | postgres:15-alpine (pública) | Banco de dados PostgreSQL |

- Rede Docker: `rede-dimdim`
- Volume nomeado: `pgdata-dimdim`
- Usuário da app: `dimdimuser` (não-root)
- Workdir: `/dimdimapp`

---

## ☁️ How To — Executando na Nuvem (Azure VM)

### 1. Criar VM Linux no Azure

No portal Azure:
1. Crie uma VM Ubuntu 22.04 LTS (tamanho B1s é suficiente)
2. Libere as portas **22** (SSH) e **8000** (API) no Security Group
3. Conecte via SSH:

```bash
ssh azureuser@<IP_PUBLICO_DA_VM>
```

### 2. Instalar Docker na VM

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/dimdimapp.git
cd dimdimapp
```

### 4. Criar a rede Docker

```bash
docker network create rede-dimdim
```

### 5. Criar o volume nomeado

```bash
docker volume create pgdata-dimdim
```

### 6. Subir o container do banco (imagem pública, sem Dockerfile)

> ⚠️ RM já configurado: 556612

```bash
docker container run -d \
  --name db-dimdim-556612 \
  --network rede-dimdim \
  -e POSTGRES_USER=dimdim \
  -e POSTGRES_PASSWORD=dimdim123 \
  -e POSTGRES_DB=dimdimdb \
  -v pgdata-dimdim:/var/lib/postgresql/data \
  postgres:15-alpine
```

### 7. Build da imagem da aplicação

```bash
docker image build -t dimdimapp:1.0 .
```

### 8. Subir o container da aplicação (com Dockerfile personalizado)

> ⚠️ RM já configurado: 556612

```bash
docker container run -d \
  --name app-dimdim-556612 \
  --network rede-dimdim \
  -e DATABASE_URL=postgresql://dimdim:dimdim123@db-dimdim-556612:5432/dimdimdb \
  -p 8000:8000 \
  dimdimapp:1.0
```

> **Atenção:** o hostname no DATABASE_URL deve bater com o `--name` do container do banco.

### 9. Verificar containers em execução

```bash
docker container ls
```

---

## 🧪 Testes — CRUD Completo

Substitua `<IP_DA_VM>` pelo IP público da sua VM Azure.

### CREATE — Criar conta

```bash
curl -X POST http://<IP_DA_VM>:8000/contas \
  -H "Content-Type: application/json" \
  -d '{"titular": "João Silva", "cpf": "123.456.789-00", "saldo": 1500.00, "tipo": "corrente"}'
```

### READ ALL — Listar todas as contas

```bash
curl http://<IP_DA_VM>:8000/contas
```

### READ ONE — Buscar conta por ID

```bash
curl http://<IP_DA_VM>:8000/contas/1
```

### UPDATE — Atualizar saldo

```bash
curl -X PUT http://<IP_DA_VM>:8000/contas/1 \
  -H "Content-Type: application/json" \
  -d '{"saldo": 2500.00}'
```

### DELETE — Remover conta

```bash
curl -X DELETE http://<IP_DA_VM>:8000/contas/1
```

---

## 🔍 Evidências no Banco — SELECT direto no PostgreSQL

```bash
# Acessar o container do banco
docker container exec -it db-dimdim-556612 psql -U dimdim -d dimdimdb

# Dentro do psql — verificar dados após cada operação:
SELECT * FROM contas;
```

---

## 🛠️ Inspecionar containers (requisito 06)

```bash
# Container da aplicação
docker container exec -it app-dimdim-556612 bash -c "pwd && ls -la && whoami"

# Container do banco
docker container exec -it db-dimdim-556612 sh -c "pwd && ls && whoami"
```

---

## 📖 Documentação interativa da API

Acesse no browser:

```
http://<IP_DA_VM>:8000/docs
```

---

## 🔒 Boas Práticas Implementadas

- ✅ Usuário não-root (`dimdimuser`) no container da aplicação
- ✅ Variável de ambiente `DATABASE_URL` configurável
- ✅ Volume nomeado para persistência do PostgreSQL
- ✅ Rede Docker isolada (`rede-dimdim`)
- ✅ Imagem base slim (menos vulnerabilidades)
- ✅ Dependências instaladas antes do código (cache de layers)
- ✅ CRUD completo com tabela `contas`
