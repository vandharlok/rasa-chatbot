<h1>Chatbot para Clínica Médica</h1>
<p>Este repositório contém um chatbot desenvolvido com o framework Rasa, projetado para facilitar o atendimento em clínicas médicas. O bot pode responder perguntas frequentes e agendar consultas diretamente no Google Calendar.</p>

<h2>Funcionalidades</h2>
<ul>
  <li><strong>Responder FAQs</strong>: Fornece respostas instantâneas às perguntas mais frequentes dos pacientes.</li>
  <li><strong>Agendamento de Consultas</strong>: Integra-se com a API do Google Calendar para marcar consultas diretamente através do chat.</li>
</ul>

<p>Recomendo utilizar um ambiente como anaconda ou miniconda, e criar um ambiente python na versão 3.9 para não ter problemas com incompatibilidades:</p>
<code>
conda create --name projeto python=3.9
</code>

<h2>Pré-requisitos</h2>
<p>Antes de iniciar, você precisará instalar:</p>
<ul>
  <li>Docker</li>
  <li>Docker Compose</li>
  <li>Node.js</li>
  <li>Sequelize CLI</li>
</ul>

Para utilização do algoritmo duckling na pipeline, o qual e resposavel por extrair as entidades de data, instale docker no seu pc e faça o pull do rasa/duckling dessa forma:

docker pull rasa/duckling
docker run -p 8000:8000 rasa/duckling


<h2>Configuração do Ambiente</h2>
<h3>Docker e Docker Compose</h3>
<p>Instruções para instalação:</p>
<ul>
  <li>Incluído no Docker Desktop para Windows e Mac.</li>
  <li>Para Linux, siga estas <a href="https://docs.docker.com/compose/install/">instruções</a>.</li>
</ul>

<h3>Node.js e Sequelize CLI</h3>
<p><strong>Node.js</strong>: Pode ser baixado e instalado a partir <a href="https://nodejs.org/">daqui</a>.</p>
<p><strong>Sequelize CLI</strong>: Após instalar o Node.js, instale o Sequelize CLI globalmente usando npm:</p>
<code>
npm install -g sequelize-cli
</code>

<h2>Configuração da API do Google Calendar</h2>
<p>Para integrar o chatbot com o Google Calendar, você precisará de um token de acesso, que será criado na raiz do projeto para que ele possa funcionar:</p>
<ul>
  <li>Acesse o <a href="https://console.developers.google.com/">Google Developers Console</a>.</li>
  <li>Crie um novo projeto.</li>
  <li>Ative a API do Google Calendar.</li>
  <li>Crie credenciais para acessar a API.</li>
  <li>Baixe o arquivo JSON das credenciais e guarde-o de forma segura.</li>
</ul>

<h2>Instalação e Execução</h2>
<p>Clone o repositório:</p>
<code>
git clone &lt;URL_DO_REPOSITORIO&gt;
cd &lt;NOME_DO_REPOSITORIO&gt;
</code>

<p>Instale as dependências do Rasa:</p>
<code>
pip install -r requirements.txt
</code>

<p>Inicie os serviços usando Docker Compose:</p>
<code>
docker-compose up -d --build
</code>

Você pode analisar o desempenho do chatbot, como f1-score, recall, accuracy, loss, t-loss, utilizando o tensorboard, o projeto ja tem o tensorboard monitorando na pipeline, para obter as métricas, basta instalar o tensorboard, e rodar o comando: 

pip install tensorboard

tensorboard --logdir ./tensorboard
Métricas atuais: ![image](https://github.com/vandharlok/rasa-chatbot/assets/104177726/9e6c9697-a296-4fd2-8819-c27c2dacaa36)
![image](https://github.com/vandharlok/rasa-chatbot/assets/104177726/3e43f652-0dbe-4271-9bc6-0614f399f196)

Desempenhando um bom acc e loss diminuindo com o tempo.


<h3>Configuração do Nginx para o frontend</h3>
<p>As configurações de Nginx estão localizadas no diretório <strong>nginx</strong>.</p>
<p>Certifique-se de que o Nginx está configurado para servir o frontend estático e redirecionar adequadamente as solicitações para o backend do chatbot.</p>
<p>Acesse o chatbot através do navegador em <a href="http://localhost:3001">http://localhost:3001</a></p>

<h2>Suporte</h2>
<p>Para obter ajuda com a configuração ou uso do chatbot, abra uma issue neste repositório.</p>

<p>Este exemplo cobre a instalação e a configuração básica. Certifique-se de ajustar as instruções conforme necessário para o seu projeto específico, especialmente no que se refere aos caminhos dos diretórios e configurações específicas do seu ambiente.</p>
