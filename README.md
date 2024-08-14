<h1>Chatbot para Clínica Médica</h1>
<p>Este repositório contém um chatbot desenvolvido com o framework Rasa, projetado para facilitar o atendimento em clínicas médicas. O bot pode responder perguntas frequentes e agendar consultas diretamente no Google Calendar / API propria de calendario.</p>

<h2>Funcionalidades</h2>
<ul>
  <li><strong>Responder FAQs</strong>: Fornece respostas instantâneas às perguntas mais frequentes dos pacientes.</li>
  <li><strong>Agendamento de Consultas</strong>: Integra-se com a API do Google Calendar, e também a API própria do calendario frontend, para marcar consultas diretamente através do chat.</li>
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


<h2>Configuração da API do Google Calendar</h2>
<p>Para integrar o chatbot com o Google Calendar, você precisará de um token de acesso, que será criado na raiz do projeto para que ele possa funcionar:</p>
<ul>
  <li>Acesse o <a href="https://console.developers.google.com/">Google Developers Console</a>.</li>
  <li>Crie um novo projeto.</li>
  <li>Ative a API do Google Calendar.</li>
  <li>Entenda melhor sobre a API em <a href= "https://developers.google.com/calendar/api/quickstart/python?hl=pt-br">API CALENDAR </a>. </li>
  <li>Crie credenciais para acessar a API.</li>
  <li>Voce precisara do <strong>token.pickle</strong> e as <strong>credentials.json</strong> em seu no diretorio main, pois e usado nas actions para funcionamento da API do Google Calendar</li>
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
<strong>Métricas atuais: </strong>

![image](https://github.com/vandharlok/rasa-chatbot/assets/104177726/9e6c9697-a296-4fd2-8819-c27c2dacaa36)
![image](https://github.com/vandharlok/rasa-chatbot/assets/104177726/3e43f652-0dbe-4271-9bc6-0614f399f196)


<strong> Desempenhando um bom acc e loss diminuindo com o tempo. </strong>


<h2>Suporte</h2>
<p>Para obter ajuda com a configuração ou uso do chatbot, abra uma issue neste repositório.</p>

<p>Este exemplo cobre a instalação e a configuração básica. Certifique-se de ajustar as instruções conforme necessário para o seu projeto específico, especialmente no que se refere aos caminhos dos diretórios e configurações específicas do seu ambiente.</p>


<strong>O codigo do backend, frontend calendar, frontend chatbot, não está disponivel nesse código, para mais informações sobre o projeto todo, por favor, e-mail me: vandersonaugusto6@gmail.com</strong>  
<strong>O codigo de actions utiliza o backend e frontend próprio, tambem para uso do calendario, então se utilizar se quiser utilizar a API do Google Calendar, mova o arquivo actions_api_calendar para pasta actions, e substitua pelo arquivo actions.py.</strong>  

<strong>Disponibilizo um frontend para web para poder rodar o rasa no meus repositorios, chamado, front_calendar, com ele e possivel rodar o rasa no web. Com isso, basta rodar os seguintes comandos no rasa : rasa run actions, rasa run --enable-api --cors "*"</strong>  


<strong> Veja o chatbot funcionando em : </strong> 
https://www.youtube.com/watch?v=Rgx1upuoqBk
