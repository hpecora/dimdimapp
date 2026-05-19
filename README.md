# DimDimApp — CP3 DevOps Tools & Cloud Computing | FIAP

API RESTful para a Instituição Financeira DimDim, containerizada com Docker e executada em nuvem (Azure).

---

## 🌐 Deploy em Nuvem

Aplicação executada em máquina virtual Ubuntu 22.04 na Microsoft Azure.

---

## 🗂️ Estrutura do Projeto


dimdimapp/
├── app/
│   ├── __init__.py
│   └── main.py          # API FastAPI (CRUD completo)
├── Dockerfile           # Imagem da aplicação
├── requirements.txt
└── README.md

🐳 Arquitetura Docker

Container	Imagem	Papel
api-dimdim-556612	Custom (Dockerfile)	API FastAPI Python
db-dimdim-556612	postgres:15-alpine (pública)	Banco de dados PostgreSQL
Rede Docker: rede-dimdim
Volume nomeado: pgdata-dimdim
Usuário da app: dimdimuser (não-root)
Workdir: /dimdimapp

☁️ How To — Executando na Nuvem (Azure VM)
1. Criar VM Linux no Azure

No portal Azure:

Crie uma VM Ubuntu 22.04 LTS (tamanho B1s é suficiente)
Libere as portas 22 (SSH) e 8000 (API) no Security Group
Conecte via SSH:
ssh azureuser@<IP_PUBLICO_DA_VM>

2. Instalar Docker na VM
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

3. Clonar o repositório
git clone https://github.com/hpecora/dimdimapp.git
cd dimdimapp

4. Criar a rede Docker
docker network create rede-dimdim

5. Criar o volume nomeado
docker volume create pgdata-dimdim

6. Subir o container do banco (imagem pública, sem Dockerfile)


docker container run -d \
  --name db-dimdim-556612 \
  --network rede-dimdim \
  -e POSTGRES_USER=azureuser \
  -e POSTGRES_PASSWORD=DimDim@20261 \
  -e POSTGRES_DB=dimdimdb \
  -v pgdata-dimdim:/var/lib/postgresql/data \
  postgres:15-alpine
  
7. Build da imagem da aplicação
docker image build -t dimdimapp:1.0 .

8. Subir o container da aplicação (com Dockerfile personalizado)

docker container run -d \
  --name api-dimdim-556612 \
  --network rede-dimdim \
  -e DATABASE_URL=postgresql://dimdim:dimdim123@db-dimdim-556612:5432/dimdimdb \
  -p 8000:8000 \
  dimdimapp:1.0

9. Verificar containers em execução
docker container ls

🧪 Testes — CRUD Completo

Substitua <IP_DA_VM> pelo IP público da sua VM Azure.

CREATE — Criar conta
curl -X POST http://<IP_DA_VM>:8000/contas \
  -H "Content-Type: application/json" \
  -d '{"titular": "João Silva", "cpf": "12345678900", "saldo": 1500.00, "tipo": "corrente"}'
  
READ ALL — Listar todas as contas
curl http://<IP_DA_VM>:8000/contas

READ ONE — Buscar conta por ID
curl http://<IP_DA_VM>:8000/contas/1

UPDATE — Atualizar saldo
curl -X PUT http://<IP_DA_VM>:8000/contas/1 \
  -H "Content-Type: application/json" \
  -d '{"saldo": 2500.00}'
  
DELETE — Remover conta
curl -X DELETE http://<IP_DA_VM>:8000/contas/1


🔍 Evidências no Banco — SELECT direto no PostgreSQL
# Acessar o container do banco
docker container exec -it db-dimdim-556612 sh

# Entrar no PostgreSQL
psql -U dimdim -d dimdimdb

# Verificar dados após cada operação
SELECT * FROM contas;
🛠️ Inspecionar containers (requisito 06)
Container da aplicação
docker container exec -it api-dimdim-556612 sh

Dentro do container:

whoami
pwd
ls

Container do banco
docker container exec -it db-dimdim-556612 sh

Dentro do container:

whoami
pwd
ls
📖 Documentação interativa da API

Acesse no navegador:

http://<IP_DA_VM>:8000/docs
🔒 Boas Práticas Implementadas
✅ Usuário não-root (dimdimuser) no container da aplicação
✅ Variável de ambiente DATABASE_URL
✅ Volume nomeado para persistência do PostgreSQL
✅ Rede Docker isolada (rede-dimdim)
✅ Imagem base slim
✅ CRUD completo com tabela contas
✅ Containers executando em background
✅ Aplicação executando em nuvem (Azure)


👨‍💻 Integrantes
Henrique Pecora — RM556612
Santhiago — RM98420

🎥 Vídeo Demonstrativo

Link do vídeo no YouTube:

https://youtu.be/4FHmJoPd1K0?si=7mOKxtRb2p5hA3WG
