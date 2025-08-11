"""
# Atualizador de Aplicativos via Winget (GUI)

Este projeto é uma aplicação em Python com interface gráfica usando Tkinter
para atualizar todos os aplicativos disponíveis no sistema utilizando o
gerenciador de pacotes **winget** do Windows.

A aplicação exibe logs em tempo real, barra de progresso e mensagens de status
para facilitar o acompanhamento do processo.

--------------------------------------------------
📌 Funcionalidades
--------------------------------------------------
- Interface gráfica simples e intuitiva
- Verificação automática se o 'winget' está instalado
- Execução do comando:
    winget upgrade --all --accept-source-agreements --accept-package-agreements --silent
- Log detalhado com timestamp
- Barra de progresso indeterminada durante a atualização
- Captura e exibição da saída do winget em tempo real
- Mensagens de sucesso, aviso ou erro ao final da execução

--------------------------------------------------
📂 Estrutura do Projeto
--------------------------------------------------
.
├── log_atualizacao_apps.txt   # Arquivo de log gerado automaticamente
├── app.py                     # Código principal da aplicação
└── README.md                  # Este arquivo

--------------------------------------------------
⚙️ Requisitos
--------------------------------------------------
- Python 3.8+ instalado
- Windows 10 ou 11
- Winget instalado e configurado no PATH
    Se o 'winget' não estiver disponível, baixe-o pelo site oficial da Microsoft
    ou via atualização do Windows.

--------------------------------------------------
📦 Instalação
--------------------------------------------------
1. Clone ou baixe este repositório.
2. Abra um terminal na pasta do projeto.
3. Execute:
    python app.py

--------------------------------------------------
▶️ Como Usar
--------------------------------------------------
1. Abrir o programa (python app.py)
2. Se o 'winget' estiver instalado, aparecerá a mensagem:
    Executando 'winget upgrade --all'...
    Clique em 'Atualizar todos' para iniciar.
3. Clique no botão "Atualizar todos" para iniciar o processo.
4. Acompanhe o progresso na tela:
    - "Atualizações em andamento" → status geral
    - "Saída do winget" → logs detalhados
5. Ao final, será exibida uma mensagem de conclusão ou erro.

--------------------------------------------------
📜 Log de Execução
--------------------------------------------------
O arquivo 'log_atualizacao_apps.txt' registra:
- Data e hora da execução
- Status da verificação do winget
- Início e fim da atualização
- Mensagens de erro, se houver

Exemplo:
========== 2025-08-11 15:30:12 ==========
Winget verificado: INSTALADO.

========== 2025-08-11 15:31:05 ==========
Processo 'winget upgrade --all' finalizado com código: 0

--------------------------------------------------
🛠 Tecnologias Utilizadas
--------------------------------------------------
- Python – linguagem principal
- Tkinter – interface gráfica
- threading – execução em segundo plano
- subprocess – execução de comandos do sistema
- queue – comunicação segura entre threads
- winget – gerenciador de pacotes do Windows

--------------------------------------------------
⚠️ Observações
--------------------------------------------------
- Necessário executar em Windows com 'winget' instalado.
- A execução como Administrador pode ser necessária para alguns pacotes.
- O log é salvo no mesmo diretório do script.

--------------------------------------------------
📄 Licença
--------------------------------------------------
Este projeto é de uso livre para fins educacionais e pessoais.
"""
