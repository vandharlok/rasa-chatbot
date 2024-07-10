<h1>Chatbot para Clínica Médica</h1>
Este repositório contém um chatbot desenvolvido com o framework Rasa, projetado para facilitar o atendimento em clínicas médicas. O bot pode responder perguntas frequentes e agendar consultas diretamente no Google Calendar.

Funcionalidades
Responder FAQs: Fornece respostas instantâneas às perguntas mais frequentes dos pacientes.
Agendamento de Consultas: Integra-se com a API do Google Calendar para marcar consultas diretamente através do chat.
Pré-requisitos
Antes de iniciar, você precisará instalar:

Docker
Docker Compose
Node.js
Sequelize CLI
Configuração do Ambiente
Docker e Docker Compose
Instalação do Docker:

Windows e Mac: Baixe o instalador do Docker Desktop aqui.
Linux: Siga as instruções específicas para a sua distribuição aqui.
Instalação do Docker Compose:

Incluído no Docker Desktop para Windows e Mac.
Para Linux, siga estas instruções.
Node.js e Sequelize CLI
Node.js: Pode ser baixado e instalado a partir daqui.
Sequelize CLI: Após instalar o Node.js, instale o Sequelize CLI globalmente usando npm:
bash
Copiar código
npm install -g sequelize-cli
Configuração da API do Google Calendar
Para integrar o chatbot com o Google Calendar, você precisará de um token de acesso:

Acesse o Google Developers Console.
Crie um novo projeto.
Ative a API do Google Calendar.
Crie credenciais para acessar a API.
Baixe o arquivo JSON das credenciais e guarde-o de forma segura.
Instalação e Execução
Clone o repositório:

bash
Copiar código
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
Instale as dependências do Rasa:

bash
Copiar código
pip install -r requirements.txt
Inicie os serviços usando Docker Compose:

bash
Copiar código
docker-compose up --build
Configuração do Nginx para o frontend:

As configurações de Nginx estão localizadas no diretório nginx.
Certifique-se de que o Nginx está configurado para servir o frontend estático e redirecionar adequadamente as solicitações para o backend do chatbot.
Acesse o chatbot através do navegador em http://localhost.

Suporte
Para obter ajuda com a configuração ou uso do chatbot, abra uma issue neste repositório.

Este exemplo cobre a instalação e a configuração básica. Certifique-se de ajustar as instruções conforme necessário para o seu projeto específico, especialmente no que se refere aos caminhos dos diretórios e configurações específicas do seu ambiente.
