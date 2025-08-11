import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import queue
import os
from datetime import datetime

# --- Configurações e Log ---
LOG_FILENAME = "log_atualizacao_apps.txt"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILENAME)

def escreve_log(txt):
    """Escreve uma entrada no arquivo de log com timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*10} {timestamp} {'='*10}\n{txt}\n")
    except Exception as e:
        # Se não conseguir escrever no log, apenas imprime no console
        print(f"ERRO AO ESCREVER LOG ({timestamp}): {e}\n{txt}")

# --- Funções de Utilitário ---
def winget_instalado():
    """Verifica se o winget está disponível no PATH."""
    try:
        # Usamos DEVNULL para não poluir o stdout/stderr do console
        subprocess.run(["winget", "--version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW
                      )
        escreve_log("Winget verificado: INSTALADO.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        escreve_log("Winget verificado: NÃO ENCONTRADO ou ERRO.")
        return False
    except Exception as e:
        escreve_log(f"Erro inesperado na verificação do winget: {e}")
        return False

# --- Classe Principal da Aplicação GUI ---
class AppUpdater:
    def __init__(self, master):
        self.master = master
        master.title("Atualizador de Apps (winget)")
        master.geometry("700x550")
        master.configure(bg="#0B0C2A")

        # Fila para comunicação thread -> GUI
        self.queue = queue.Queue()

        # --- Widgets da GUI ---
        tk.Label(master, text="Atualizações em andamento:",
                 bg="#0B0C2A", fg="white", font=("Arial",10,"bold")
        ).pack(pady=(20,5))

        self.txt_dispo = tk.Text(master, height=8, width=80,
                                 font=("Consolas",9), bg="white", fg="black",
                                 bd=0, relief="flat")
        self.txt_dispo.pack()
        scrollbar_dispo = ttk.Scrollbar(master, command=self.txt_dispo.yview)
        scrollbar_dispo.pack(side="right", fill="y")
        self.txt_dispo['yscrollcommand'] = scrollbar_dispo.set

        tk.Label(master, text="Progresso:",
                 bg="#0B0C2A", fg="white", font=("Arial",10,"bold")
        ).pack(pady=(10, 5))
        # Barra de Progresso Indeterminada
        self.pb = ttk.Progressbar(master, length=600, mode="indeterminate")
        self.pb.pack(pady=(0, 10))

        tk.Label(master, text="Saída do winget:",
                 bg="#0B0C2A", fg="white", font=("Arial",10,"bold")
        ).pack(pady=(10, 5))
        self.txt_log  = tk.Text(master, height=10, width=80,
                                font=("Consolas",9), bg="black", fg="lime",
                                bd=0, relief="flat")
        self.txt_log.pack()
        scrollbar_log = ttk.Scrollbar(master, command=self.txt_log.yview)
        scrollbar_log.pack(side="right", fill="y")
        self.txt_log['yscrollcommand'] = scrollbar_log.set

        self.btn = tk.Button(master, text="Atualizar todos",
                             font=("Arial",12,"bold"),
                             bg="#D35400", fg="white",
                             command=self.start_update)
        self.btn.pack(pady=20)

        # --- Inicialização ---
        # O botão começa habilitado
        self.btn.config(state="normal")

        # Verifica winget
        if not winget_instalado():
            msg = "❌ O comando 'winget' não foi encontrado no sistema."
            self.txt_dispo.insert("end", msg)
            messagebox.showerror("Erro", msg)
            self.btn.config(state="normal")  # Habilita mesmo com erro
        else:
            # Mensagem inicial para informar sobre o winget upgrade --all
            self.txt_dispo.insert("end", "Executando 'winget upgrade --all'...\nClique em 'Atualizar todos' para iniciar.")

        # Inicia o loop periódico para processar a fila de mensagens
        self.master.after(100, self._processa_queue)


    # --- Métodos de Atualização (Thread) ---
    def start_update(self):
        """Inicia a thread que chama winget upgrade --all."""
        self.btn.config(state="disabled") # Desabilita o botão
        self.txt_log.delete("1.0", tk.END) # Limpa o log
        self.txt_dispo.delete("1.0", tk.END) # Limpa a mensagem
        self.pb.config(mode="indeterminate") # Inicia barra indeterminada
        self.pb.start(20)  # Inicia a animação (intervalo em milissegundos)
        escreve_log("Iniciando thread de atualização (winget upgrade --all).")
        t = threading.Thread(target=self._thread_updater, daemon=True)
        t.start()

    def _thread_updater(self):
        """Thread para executar winget upgrade --all e capturar saída."""
        try:
            escreve_log("Executando winget upgrade --all")
            cmd = [
              "winget", "upgrade", "--all",
              "--accept-source-agreements",
              "--accept-package-agreements",
              "--silent"
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW)

            for linha in proc.stdout:
                self.queue.put(("log", linha)) # Envia cada linha para o log

            proc.wait()
            exit_code = proc.returncode
            self.queue.put(("done", exit_code))
            escreve_log(f"Processo 'winget upgrade --all' finalizado com código: {exit_code}")

        except FileNotFoundError:
            msg = "Erro: winget não encontrado durante a atualização."
            escreve_log(msg)
            self.queue.put(("error_update", msg))
        except Exception as e:
            msg = f"Erro inesperado durante a atualização: {e}"
            escreve_log(msg)
            self.queue.put(("error_update", msg))

    # --- Processamento da Fila (Main Thread) ---
    def _processa_queue(self):
        """Chamada periódica para processar mensagens da fila."""
        try:
            while True:
                tipo, val = self.queue.get_nowait()

                if tipo == "log":
                    self.txt_log.insert(tk.END, val)
                    self.txt_log.see(tk.END)
                elif tipo == "done":
                    exit_code = val
                    self.pb.stop()  # Para a animação da barra
                    if exit_code == 0:
                        messagebox.showinfo("Concluído", "✅ Aplicativos atualizados com sucesso!")
                    else:
                        messagebox.showwarning("Atualização Finalizada", f"Processo finalizado com código: {exit_code}\nVerifique a 'Saída do winget' para detalhes.")
                    # Re-habilita o botão
                    self.btn.config(state="normal")
                elif tipo == "error_update":
                    self.pb.stop()  # Para a animação da barra
                    messagebox.showerror("Erro na Atualização", f"❌ Ocorreu um erro durante a atualização:\n{val}")
                    # Re-habilita o botão
                    self.btn.config(state="normal")

        except queue.Empty:
            pass
        except Exception as e:
            escreve_log(f"Erro inesperado ao processar fila na thread principal: {e}")
            # Manter o botão habilitado
            pass
        finally:
            self.master.after(100, self._processa_queue)

    def _atualizar_lista_disponiveis_gui(self, data):
        """Não usado no winget upgrade --all, mas mantido por compatibilidade."""
        self.txt_dispo.delete("1.0", tk.END)
        self.txt_dispo.insert("end", "Executando 'winget upgrade --all'...\nClique em 'Atualizar todos' para iniciar.")
        self.btn.config(state="normal")  # Garante que o botão esteja habilitado

# --- Início da aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AppUpdater(root)
    root.mainloop()
