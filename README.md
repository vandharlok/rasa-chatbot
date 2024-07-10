<h1>Chatbot para Clínica Médica</h1>
Este repositório contém um chatbot desenvolvido com o framework Rasa, projetado para facilitar o atendimento em clínicas médicas. O bot pode responder perguntas frequentes e agendar consultas diretamente no Google Calendar.

<strong>Funcionalidades</strong>
Responder FAQs: Fornece respostas instantâneas às perguntas mais frequentes dos pacientes.
Agendamento de Consultas: Integra-se com a API do Google Calendar para marcar consultas diretamente através do chat.

Recomendo utilizar um ambiente como anaconda, miniconda, e criar um ambiente python na versão 3.9 para não ter problemas com incompartibilidades
Para isso, instale o miniconda, e crie um projeto dessa forma:

conda create --name projeto python=3.9


Pré-requisitos
Antes de iniciar, você precisará instalar:


Docker
Docker Compose
Node.js
Sequelize CLI
Configuração do Ambiente
Docker e Docker Compose
Instalação do Docker:

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
Para integrar o chatbot com o Google Calendar, você precisará de um token de acesso, que sera criado na raiz do projeto para que ele possa funcionar:

Acesse o Google Developers Console.
Crie um novo projeto.
Ative a API do Google Calendar.
Crie credenciais para acessar a API.
Baixe o arquivo JSON das credenciais e guarde-o de forma segura.
Instalação e Execução
Clone o repositório:

Instale as dependências do Rasa:

pip install -r requirements.txt

Inicie os serviços usando Docker Compose:

docker compose up -d --build

Configuração do Nginx para o frontend:

<strong>Desempenho</strong>
Você pode analisar o desempenho do chatbot, como f1-score, recall, accuracy, loss, t-loss, utilizando o tensorboard, o projeto ja tem o tensorboard monitorando na pipeline, para obter as métricas, basta instalar o tensorboard, e rodar o comando: 

pip install tensorboard

tensorboard --logdir ./tensorboard


As configurações de Nginx estão localizadas no diretório nginx.
Certifique-se de que o Nginx está configurado para servir o frontend estático e redirecionar adequadamente as solicitações para o backend do chatbot.
Acesse o chatbot através do navegador em http://localhost:3001

Suporte
Para obter ajuda com a configuração ou uso do chatbot, abra uma issue neste repositório.

Este exemplo cobre a instalação e a configuração básica. Certifique-se de ajustar as instruções conforme necessário para o seu projeto específico, especialmente no que se refere aos caminhos dos diretórios e configurações específicas do seu ambiente.
