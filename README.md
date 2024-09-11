<h1>Chatbot para Clínica Médica</h1>
<p>Este repositório contém um chatbot desenvolvido com o framework Rasa, projetado para facilitar o atendimento em clínicas médicas. O bot pode responder perguntas frequentes, agendar consultas, remarcar consultas, cancelar consultas, diretamente no Google Calendar / API propria de calendario.</p>

<h2>Funcionalidades</h2>
<ul>
  <li><strong>Responder FAQs</strong>: Fornece respostas instantâneas às perguntas mais frequentes dos pacientes.</li>
  <li><strong>Agendamento de Consultas</strong>: Integra-se com a API do Google Calendar, e também a API própria do calendario</li>
</ul>

<p>Utilizar um ambiente como anaconda ou miniconda, e criar um ambiente python na versão 3.9 para não ter problemas com incompatibilidades:</p>
<code>
conda create --name chatbot python=3.9
</code>

<h2>Pré-requisitos</h2>
<p>Antes de iniciar, basta voce instalar os requirements:</p>
<ul>
  <li>pip install -r requirements_txt</li>
  <li>pip install -r requirements_actions_txt</li>
  <li>pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_md-3.7.0/pt_core_news_md-3.7.0.tar.gz</li>
</ul>

Para utilização do algoritmo duckling na pipeline, o qual e resposavel por extrair as entidades de data, instale docker no seu pc e faça o pull do rasa/duckling dessa forma:

docker pull rasa/duckling
docker run -p 8000:8000 rasa/duckling

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

<h2>Execução</h2>
<p>Para pode rodar o rasa core and rasa nlu</p>
<ul>
  <li>rasa train</li>
  <li>rasa run actions</li>
  <li>rasa shell </li>
</ul>

Você pode analisar o desempenho do chatbot, como f1-score, recall, accuracy, loss, t-loss, utilizando o tensorboard, o projeto ja tem o tensorboard monitorando na pipeline, para obter as métricas, basta instalar o tensorboard, e rodar o comando: 

pip install tensorboard

tensorboard --logdir ./tensorboard

<h2>Suporte</h2>
<p>Para obter ajuda com a configuração ou uso do chatbot, abra uma issue neste repositório.</p>

<p>Este exemplo cobre a instalação e a configuração básica. Certifique-se de ajustar as instruções conforme necessário para o seu projeto específico, especialmente no que se refere aos caminhos dos diretórios e configurações específicas do seu ambiente.</p>

<h2>Metricas</h2>
<p>Ultimas atualizacoes das metricas de desempenho do chatbot</p>
<ul>
  
<img src = "https://github.com/user-attachments/assets/f6ebebb3-bf34-4378-935f-e7351d4604e3)">
<img src = "https://github.com/user-attachments/assets/20282e46-9ad1-48aa-b4d4-5f0e5b0f5e14) ">
</ul>



<strong>Para mais informações sobre o projeto todo, por favor, e-mail me: vandersonaugusto6@gmail.com</strong>  


<strong>Disponibilizo um frontend para web para poder rodar o rasa no meus repositorios, chamado, front_calendar, com ele e possivel rodar o rasa no web. Com isso, basta rodar os seguintes comandos no rasa : rasa run actions, rasa run --enable-api --cors "*"</strong>  


<strong> Veja o chatbot funcionando em : </strong> 
https://www.youtube.com/watch?v=Rgx1upuoqBk
