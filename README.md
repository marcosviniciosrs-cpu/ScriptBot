# 🤖 ScriptBot (MHK)

Gerenciador de scripts e macros Python que roda diretamente na **System Tray** (bandeja do sistema). Desenvolvido em **Python** com **PyQt5**.

### 🚀 Funcionalidades
* **Menu Dinâmico**: Lê pastas e arquivos `.py` automaticamente ao clicar no ícone.
* **Gerenciador de Processos**: Lista macros ativos e permite encerrá-los individualmente.
* **Interface Nativa**: Ícone desenhado via código (QPainter) para seguir o padrão visual do sistema.
* **Multiplataforma**: Compatível com Linux (Cinnamon/GNOME) e Windows.

### 🛠️ Requisitos
* Python 3.x
* PyQt5 (`pip install PyQt5`)

### 📂 Como usar
1. Coloque seus scripts na pasta `/macros`.
2. Subpastas viram submenus automaticamente para melhor organização.
3. Clique com o botão direito no robô para gerenciar suas automações.
