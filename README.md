# Top Decked Backend


---
## 🚀 Instalação  

Passo a passo de como instalar e executar o sistema.  

### **1️⃣Instalação do Postgres pelo Docker** 

[Link](https://felixgilioli.medium.com/como-rodar-um-banco-de-dados-postgres-com-docker-6aecf67995e1)
docker run -d -p 5433:5432 -e POSTGRES_PASSWORD=1234 -e POSTGRES_USER=postgres -e TZ=America/Fortaleza postgres

### **2️⃣ Clonar o repositório**  
```sh
git clone https://github.com/top-deck/top-decked-backend.git
cd top-decked-backend
```

### **3️⃣ Criar e ativar o ambiente virtual**  
```sh
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### **4️⃣ Instalar dependências**  
```sh
pip install -r requirements.txt
```

### **5️⃣ Configurar variáveis de ambiente**  
Crie um arquivo `.env` na raiz do projeto e adicione:  
```
```