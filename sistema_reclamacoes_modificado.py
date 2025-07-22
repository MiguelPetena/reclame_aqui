import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from datetime import datetime
import smtplib
import random
import time
from email.mime.text import MIMEText

class SistemaReclamacoes:
    def __init__(self):
        self.EMAIL_REMETENTE = "maikoncleber988@gmail.com"
        self.SENHA_EMAIL = "ttoj nhgy iudf xpub"
        
        self.criar_tabelas()
        self.iniciar_interface()

    def conectar_banco(self):
        return sqlite3.connect("db_reclame.db")
    
    def criar_tabelas(self):
        conn = self.conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_usuario (
            ID_USER INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome_Usuario TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Senha TEXT NOT NULL,
            ID_Cliente INTEGER UNIQUE,
            ID_Empresa INTEGER UNIQUE,
            Data_Cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Token TEXT,
            Token_Expira TIMESTAMP,
            FOREIGN KEY (ID_Empresa) REFERENCES tb_empresa(ID_Empresa)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_empresa (
            ID_Empresa INTEGER PRIMARY KEY,
            Nome_Empresa TEXT NOT NULL,
            CNPJ TEXT UNIQUE,
            ID_Representante INTEGER NOT NULL UNIQUE,
            Data_Cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_Representante) REFERENCES tb_usuario(ID_USER)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_reclamacoes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT NOT NULL,
            Descricao TEXT NOT NULL,
            Resposta TEXT,
            Status TEXT DEFAULT 'Pendente',
            ID_Cliente INTEGER NOT NULL,
            ID_Empresa INTEGER NOT NULL,
            Data_Criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Data_Resposta TIMESTAMP,
            FOREIGN KEY (ID_Cliente) REFERENCES tb_usuario(ID_Cliente),
            FOREIGN KEY (ID_Empresa) REFERENCES tb_empresa(ID_Empresa)
        )
        """)

        conn.commit()
        conn.close()
        
    def enviar_email(self, destinatario, codigo):
        """Envia e-mail com código de recuperação"""
        msg = MIMEText(f"Seu código de recuperação é: {codigo}\n\nEste código é válido por 10 minutos.", _charset="utf-8")
        msg["Subject"] = "Recuperação de Senha - Sistema de Reclamações"
        msg["From"] = self.EMAIL_REMETENTE
        msg["To"] = destinatario
        
        try:
            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(self.EMAIL_REMETENTE, self.SENHA_EMAIL)
            servidor.sendmail(self.EMAIL_REMETENTE, destinatario, msg.as_string())
            servidor.quit()
            return True
        except Exception as e:
            print("Erro ao enviar e-mail:", e)
            return False
        
    def iniciar_interface(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Reclamações")
        self.interface_login()
        self.root.mainloop()

    def validar_cnpj(self, cnpj):
        import re
        cnpj = re.sub(r'\D', '', cnpj)
        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False

        def calcular_digito(cnpj, peso):
            soma = sum(int(cnpj[i]) * peso[i] for i in range(len(peso)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        peso2 = [6] + peso1

        digito1 = calcular_digito(cnpj[:12], peso1)
        digito2 = calcular_digito(cnpj[:12] + digito1, peso2)
        return cnpj[-2:] == digito1 + digito2


    def interface_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.state("zoomed")
        self.root.title("Login - Sistema de Reclamações")

        tk.Label(self.root, text="Email:").pack(pady=(100, 5))
        self.entry_email = tk.Entry(self.root, width=30)
        self.entry_email.pack()

      
        frame_senha = tk.Frame(self.root)
        frame_senha.pack(pady=5)
        
        tk.Label(frame_senha, text="Senha:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_senha = tk.Entry(frame_senha, show="*", width=30)
        self.entry_senha.pack(side=tk.LEFT)
     
        self.var_mostrar_senha_login = tk.BooleanVar(value=False)
        self.btn_mostrar_senha_login = tk.Checkbutton(
            frame_senha, 
            text="Mostrar", 
            variable=self.var_mostrar_senha_login,
            command=lambda: self.mostrar_ocultar_senha(
                self.entry_senha, 
                self.var_mostrar_senha_login
            )
        )
        self.btn_mostrar_senha_login.pack(side=tk.LEFT, padx=(5, 0))

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Login", command=self.tentar_login).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cadastrar", command=self.cadastro_interface).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Esqueci a senha", command=self.recuperar_senha_interface).pack(side=tk.LEFT, padx=10)

    def mostrar_ocultar_senha(self, entry, var):
        """Alterna entre mostrar e ocultar o texto da senha"""
        if var.get():
            entry.config(show="")
        else:
            entry.config(show="*")

    def recuperar_senha_interface(self):
        """Interface gráfica para recuperação de senha"""
        self.recup_window = tk.Toplevel(self.root)
        self.recup_window.title("Recuperação de Senha")
        self.recup_window.geometry("1280x720")
        self.recup_window.transient(self.root)
        self.recup_window.grab_set()

        tk.Label(self.recup_window, text="Recuperação de Senha", font=('Arial', 14)).pack(pady=10)

        tk.Label(self.recup_window, text="Email cadastrado:").pack(pady=5)
        self.entry_rec_email = tk.Entry(self.recup_window, width=30)
        self.entry_rec_email.pack()

        tk.Button(self.recup_window, text="Enviar Código", command=self.enviar_codigo_recuperacao).pack(pady=10)

        tk.Label(self.recup_window, text="Código de verificação:").pack(pady=5)
        self.entry_rec_codigo = tk.Entry(self.recup_window, width=30)
        self.entry_rec_codigo.pack()

  
        frame_nova_senha = tk.Frame(self.recup_window)
        frame_nova_senha.pack(pady=5)
        tk.Label(frame_nova_senha, text="Nova Senha:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_rec_nova_senha = tk.Entry(frame_nova_senha, show="*", width=30)
        self.entry_rec_nova_senha.pack(side=tk.LEFT)
        
    
        self.var_mostrar_nova_senha = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_nova_senha, 
            text="Mostrar", 
            variable=self.var_mostrar_nova_senha,
            command=lambda: self.mostrar_ocultar_senha(
                self.entry_rec_nova_senha, 
                self.var_mostrar_nova_senha
            )
        ).pack(side=tk.LEFT, padx=(5, 0))

      
        frame_conf_senha = tk.Frame(self.recup_window)
        frame_conf_senha.pack(pady=5)
        tk.Label(frame_conf_senha, text="Confirmar Nova Senha:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_rec_conf_senha = tk.Entry(frame_conf_senha, show="*", width=30)
        self.entry_rec_conf_senha.pack(side=tk.LEFT)
        
     
        self.var_mostrar_conf_senha = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_conf_senha, 
            text="Mostrar", 
            variable=self.var_mostrar_conf_senha,
            command=lambda: self.mostrar_ocultar_senha(
                self.entry_rec_conf_senha, 
                self.var_mostrar_conf_senha
            )
        ).pack(side=tk.LEFT, padx=(5, 0))

        btn_frame = tk.Frame(self.recup_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Redefinir Senha", command=self.redefinir_senha).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.recup_window.destroy).pack(side=tk.LEFT, padx=5)

    def enviar_codigo_recuperacao(self):
        """Envia código de recuperação para o e-mail informado"""
        email = self.entry_rec_email.get().strip().lower()
        
        if not email:
            messagebox.showerror("Erro", "Digite um e-mail válido.")
            return
            
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_USER FROM tb_usuario WHERE LOWER(Email) = ?", (email,))
        usuario = cursor.fetchone()
        conn.close()
        
        if not usuario:
            messagebox.showerror("Erro", "E-mail não cadastrado no sistema.")
            return
            
        codigo = str(random.randint(100000, 999999))
        expira_em = time.time() + 600 
        
        conn = self.conectar_banco()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE tb_usuario 
                SET Token = ?, Token_Expira = ?
                WHERE Email = ?
            """, (codigo, expira_em, email))
            conn.commit()
            
            if self.enviar_email(email, codigo):
                messagebox.showinfo("Sucesso", f"Código enviado para {email}")
            else:
                messagebox.showerror("Erro", "Falha ao enviar e-mail. Tente novamente mais tarde.")
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao gerar código: {str(e)}")
        finally:
            conn.close()

    def redefinir_senha(self):
        """Redefine a senha do usuário após verificação do código"""
        email = self.entry_rec_email.get().strip().lower()
        codigo = self.entry_rec_codigo.get().strip()
        nova_senha = self.entry_rec_nova_senha.get().strip()
        conf_senha = self.entry_rec_conf_senha.get().strip()
        
        if not all([email, codigo, nova_senha, conf_senha]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
            
        if nova_senha != conf_senha:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
            
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Token, Token_Expira 
            FROM tb_usuario 
            WHERE LOWER(Email) = ?
        """, (email,))
        resultado = cursor.fetchone()
        
        if not resultado:
            messagebox.showerror("Erro", "E-mail não encontrado.")
            conn.close()
            return
            
        token_armazenado, token_expira = resultado
        agora = time.time()
        
        if token_armazenado != codigo:
            messagebox.showerror("Erro", "Código inválido.")
            conn.close()
            return
            
        if agora > token_expira:
            messagebox.showerror("Erro", "Código expirado. Solicite um novo.")
            conn.close()
            return
            
        try:
            cursor.execute("""
                UPDATE tb_usuario 
                SET Senha = ?, Token = NULL, Token_Expira = NULL
                WHERE LOWER(Email) = ?
            """, (nova_senha, email))
            conn.commit()
            messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!")
            self.recup_window.destroy()
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao redefinir senha: {str(e)}")
        finally:
            conn.close()

    def tentar_login(self):
        email = self.entry_email.get().strip().lower()
        senha = self.entry_senha.get().strip()

        if not email or not senha:
            messagebox.showerror("Erro", "Preencha email e senha.")
            return

        usuario = self.login(email, senha)
        if usuario:
            self.root.destroy()
            if usuario['papel'] == 'empresa':
                self.menu_empresa(usuario)
            elif usuario['papel'] == 'cliente':
                self.menu_cliente(usuario)
            else:
                messagebox.showerror("Erro", "Usuário sem papel definido.")
        else:
            messagebox.showerror("Erro", "Credenciais inválidas.")

    def login(self, email, senha):
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_USER, Nome_Usuario, ID_Empresa, ID_Cliente 
            FROM tb_usuario 
            WHERE LOWER(Email) = LOWER(?) AND Senha = ?
        """, (email, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            id_user, nome, id_empresa, id_cliente = usuario
            if id_empresa is not None:
                papel = "empresa"
            elif id_cliente is not None:
                papel = "cliente"
            else:
                papel = "indefinido"
            return {
                "id": id_user,
                "nome": nome,
                "papel": papel
            }
        return None

    def cadastro_interface(self):
        self.cadastro_window = tk.Toplevel(self.root)
        self.cadastro_window.title("Cadastro de Usuário")
        self.cadastro_window.state("zoomed")

        self.var_tipo = tk.StringVar()
        self.var_tipo.trace_add('write', self.atualizar_campos_cadastro)

        frame_principal = tk.Frame(self.cadastro_window)
        frame_principal.pack(pady=20, padx=20, fill='both', expand=True)

        tk.Label(frame_principal, text="Nome Completo:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_nome = tk.Entry(frame_principal, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Label(frame_principal, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_email_cadastro = tk.Entry(frame_principal, width=30)
        self.entry_email_cadastro.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(frame_principal, text="Senha:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        frame_senha = tk.Frame(frame_principal)
        frame_senha.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.entry_senha_cadastro = tk.Entry(frame_senha, show="*", width=30)
        self.entry_senha_cadastro.pack(side=tk.LEFT)
 
        self.var_mostrar_senha_cadastro = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_senha, 
            text="Mostrar", 
            variable=self.var_mostrar_senha_cadastro,
            command=lambda: self.mostrar_ocultar_senha(
                self.entry_senha_cadastro, 
                self.var_mostrar_senha_cadastro
            )
        ).pack(side=tk.LEFT, padx=(5, 0))

  
        tk.Label(frame_principal, text="Confirmar Senha:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        frame_conf_senha = tk.Frame(frame_principal)
        frame_conf_senha.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.entry_conf_senha_cadastro = tk.Entry(frame_conf_senha, show="*", width=30)
        self.entry_conf_senha_cadastro.pack(side=tk.LEFT)
      
        self.var_mostrar_conf_senha_cadastro = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_conf_senha, 
            text="Mostrar", 
            variable=self.var_mostrar_conf_senha_cadastro,
            command=lambda: self.mostrar_ocultar_senha(
                self.entry_conf_senha_cadastro, 
                self.var_mostrar_conf_senha_cadastro
            )
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(frame_principal, text="Tipo de Usuário:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.combo_tipo = ttk.Combobox(
            frame_principal, 
            textvariable=self.var_tipo, 
            values=["Cliente", "Empresa"], 
            state="readonly",
            width=27
        )
        self.combo_tipo.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        self.lbl_empresa_nome = tk.Label(frame_principal, text="Nome da Empresa:")
        self.entry_empresa_nome = tk.Entry(frame_principal, width=30)
        
        self.lbl_cnpj = tk.Label(frame_principal, text="CNPJ:")
        self.entry_cnpj = tk.Entry(frame_principal, width=30)
        

        tk.Button(
            frame_principal, 
            text="Cadastrar", 
            command=self.realizar_cadastro,
            width=15
        ).grid(row=7, column=0, columnspan=2, pady=20)

        tk.Label(
            frame_principal, 
            text="Campos obrigatórios", 
            font=('Arial', 10)
        ).grid(row=8, column=0, columnspan=2)

    def atualizar_campos_cadastro(self, *args):
        if self.var_tipo.get() == "Empresa":
            self.lbl_empresa_nome.grid(row=5, column=0, padx=5, pady=5, sticky='e')
            self.entry_empresa_nome.grid(row=5, column=1, padx=5, pady=5, sticky='w')
            self.lbl_cnpj.grid(row=6, column=0, padx=5, pady=5, sticky='e')
            self.entry_cnpj.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        else:
            self.lbl_empresa_nome.grid_remove()
            self.entry_empresa_nome.grid_remove()
            self.lbl_cnpj.grid_remove()
            self.entry_cnpj.grid_remove()

    def realizar_cadastro(self):
        nome_usuario = self.entry_nome.get().strip()
        email = self.entry_email_cadastro.get().strip().lower()
        senha = self.entry_senha_cadastro.get().strip()
        conf_senha = self.entry_conf_senha_cadastro.get().strip()
        tipo = self.var_tipo.get()
        nome_empresa = self.entry_empresa_nome.get().strip() if tipo == "Empresa" else ""
        cnpj = self.entry_cnpj.get().strip() if tipo == "Empresa" else ""

        if not all([nome_usuario, email, senha, conf_senha, tipo]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
            
        if senha != conf_senha:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
            
        if tipo == "Empresa" and (not nome_empresa or not cnpj):
            messagebox.showerror("Erro", "Para empresa, nome e CNPJ são obrigatórios.")
            return

        conn = self.conectar_banco()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT ID_USER FROM tb_usuario WHERE Email = ?", (email,))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Email já cadastrado.")
                return

            cursor.execute("""
                INSERT INTO tb_usuario (Nome_Usuario, Email, Senha) 
                VALUES (?, ?, ?)
            """, (nome_usuario, email, senha))
            
            id_usuario = cursor.lastrowid

            if tipo == "Cliente":
                cursor.execute("SELECT MAX(ID_Cliente) FROM tb_usuario")
                max_id = cursor.fetchone()[0] or 0
                cursor.execute("""
                    UPDATE tb_usuario 
                    SET ID_Cliente = ? 
                    WHERE ID_USER = ?
                """, (max_id + 1, id_usuario))
                
            elif tipo == "Empresa":
                cursor.execute("SELECT ID_Empresa FROM tb_empresa WHERE CNPJ = ?", (cnpj,))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "CNPJ já cadastrado.")
                    conn.rollback()
                    return
                
                cursor.execute("""
                    INSERT INTO tb_empresa (
                        ID_Empresa, 
                        Nome_Empresa, 
                        CNPJ, 
                        ID_Representante
                    ) VALUES (?, ?, ?, ?)
                """, (id_usuario, nome_empresa, cnpj, id_usuario))
             
                cursor.execute("""
                    UPDATE tb_usuario 
                    SET ID_Empresa = ? 
                    WHERE ID_USER = ?
                """, (id_usuario, id_usuario))

            conn.commit()
            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
            self.cadastro_window.destroy()

        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro no cadastro: {str(e)}")
        finally:
            conn.close()

    def menu_empresa(self, usuario):
        self.empresa_window = tk.Tk()
        self.empresa_window.title(f"Painel da Empresa - {usuario['nome']}")
        self.empresa_window.state("zoomed")

     
        frame_top = tk.Frame(self.empresa_window)
        frame_top.pack(pady=20)
        tk.Label(
            frame_top, 
            text=f"Bem-vindo(a), {usuario['nome']}", 
            font=('Arial', 14, 'bold')
        ).pack()

      
        frame_principal = tk.Frame(self.empresa_window)
        frame_principal.pack(pady=30)

    
        tk.Button(
            frame_principal, 
            text="Visualizar Reclamações", 
            command=lambda: self.ver_reclamacoes_empresa(usuario),
            width=25,
            height=3
        ).pack(pady=10)

        tk.Button(
            frame_principal, 
            text="Responder Reclamação", 
            command=lambda: self.responder_reclamacao(usuario),
            width=25,
            height=3
        ).pack(pady=10)

        tk.Button(
            frame_principal, 
            text="Sair", 
            command=self.empresa_window.destroy,
            width=25,
            height=3
        ).pack(pady=10)

    def ver_reclamacoes_empresa(self, usuario):
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ID, r.Titulo, r.Descricao, r.Status, r.Data_Criacao, 
                   u.Nome_Usuario, r.Resposta, r.Data_Resposta
            FROM tb_reclamacoes r
            JOIN tb_usuario u ON r.ID_Cliente = u.ID_Cliente
            WHERE r.ID_Empresa = ?
            ORDER BY r.Data_Criacao DESC
        """, (usuario['id'],))
        
        reclamacoes = cursor.fetchall()
        conn.close()

        reclamacoes_window = tk.Toplevel(self.empresa_window)
        reclamacoes_window.title("Reclamações Recebidas")
        reclamacoes_window.state("zoomed")

       
        frame_tree = tk.Frame(reclamacoes_window)
        frame_tree.pack(fill='both', expand=True, padx=15, pady=15)

       
        columns = ("Título", "Cliente", "Status", "Data Criação", "Descrição", "Resposta", "Data Resposta")
        tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
        
      
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='w')
        
    
        tree.column("Descrição", width=300)
        tree.column("Resposta", width=300)
        tree.column("Título", width=150)
        tree.column("Cliente", width=150)
        tree.column("Data Criação", width=120)
        tree.column("Data Resposta", width=120)

       
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)

     
        for rec in reclamacoes:
            data_criacao = datetime.strptime(rec[4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            data_resposta = datetime.strptime(rec[7], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M") if rec[7] else "Não respondida"
            
            tree.insert("", "end", values=(
               rec[1], rec[5], rec[3], 
                data_criacao, rec[2], 
                rec[6] or "Sem resposta", 
                data_resposta
            ))

    def responder_reclamacao(self, usuario):
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ID, r.Titulo, u.Nome_Usuario
            FROM tb_reclamacoes r
            JOIN tb_usuario u ON r.ID_Cliente = u.ID_Cliente
            WHERE r.ID_Empresa = ? AND r.Status = 'Pendente'
            ORDER BY r.Data_Criacao DESC
        """, (usuario['id'],))
        reclamacoes = cursor.fetchall()
        conn.close()

        if not reclamacoes:
            messagebox.showinfo("Aviso", "Nenhuma reclamação pendente para responder.")
            return

        selecao_window = tk.Toplevel(self.empresa_window)
        selecao_window.title("Selecionar Reclamação para Responder")
        selecao_window.geometry("1280x720")

        tk.Label(
            selecao_window,
            text="Selecione a reclamação para responder:",
            font=('Arial', 20)
        ).pack(pady=10)

        frame_lista = tk.Frame(selecao_window)
        frame_lista.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        lista_reclamacoes = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=('Arial', 16),
            selectbackground='#4a7abc',
            selectforeground='white'
        )

        for rec in reclamacoes:
            lista_reclamacoes.insert(tk.END, f"#{rec[0]} - {rec[1]} (Cliente: {rec[2]})")

        lista_reclamacoes.pack(fill='both', expand=True)
        scrollbar.config(command=lista_reclamacoes.yview)

        frame_botoes = tk.Frame(selecao_window)
        frame_botoes.pack(pady=10)

    def responder_reclamacao(self, usuario):
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ID, r.Titulo, u.Nome_Usuario
            FROM tb_reclamacoes r
            JOIN tb_usuario u ON r.ID_Cliente = u.ID_Cliente
            WHERE r.ID_Empresa = ? AND r.Status = 'Pendente'
            ORDER BY r.Data_Criacao DESC
        """, (usuario['id'],))
        reclamacoes = cursor.fetchall()
        conn.close()

        if not reclamacoes:
            messagebox.showinfo("Aviso", "Nenhuma reclamação pendente para responder.")
            return

        selecao_window = tk.Toplevel(self.empresa_window)
        selecao_window.title("Selecionar Reclamação para Responder")
        selecao_window.geometry("1280x720")

        tk.Label(
            selecao_window,
            text="Selecione a reclamação para responder:",
            font=('Arial', 20)
        ).pack(pady=10)

        frame_lista = tk.Frame(selecao_window)
        frame_lista.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        lista_reclamacoes = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=('Arial', 16),
            selectbackground='#4a7abc',
            selectforeground='white'
        )

        for rec in reclamacoes:
            lista_reclamacoes.insert(tk.END, f"#{rec[0]} - {rec[1]} (Cliente: {rec[2]})")

        lista_reclamacoes.pack(fill='both', expand=True)
        scrollbar.config(command=lista_reclamacoes.yview)

        frame_botoes = tk.Frame(selecao_window)
        frame_botoes.pack(pady=10)

        def confirmar_reclamacao():
            try:
                selecao = lista_reclamacoes.get(lista_reclamacoes.curselection())
                id_rec = int(selecao.split(" - ")[0][1:])
            except:
                messagebox.showerror("Erro", "Selecione uma reclamação válida.")
                return

            detalhes_window = tk.Toplevel(selecao_window)
            detalhes_window.title(f"Responder Reclamação #{id_rec}")
            detalhes_window.geometry("1280x720")

            tk.Label(
                detalhes_window,
                text=f"Responder à Reclamação #{id_rec}",
                font=('Arial', 20)
            ).pack(pady=10)

            frame_campos = tk.Frame(detalhes_window)
            frame_campos.pack(fill='both', expand=True, padx=20, pady=10)

            tk.Label(frame_campos, text="Resposta:").grid(row=0, column=0, padx=5, pady=5, sticky='ne')
            text_resposta = tk.Text(frame_campos, width=60, height=10)
            text_resposta.grid(row=0, column=1, padx=5, pady=5, sticky='w')

            def salvar_resposta():
                resposta = text_resposta.get("1.0", tk.END).strip()
                if not resposta:
                    messagebox.showerror("Erro", "A resposta não pode estar vazia.")
                    return

                try:
                    with self.conectar_banco() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE tb_reclamacoes
                            SET Resposta = ?, Status = 'Respondida', Data_Resposta = ?
                            WHERE ID = ? AND ID_Empresa = ?
                        """, (
                            resposta,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            id_rec,
                            usuario['id']
                        ))
                        conn.commit()
                        messagebox.showinfo("Sucesso", "Resposta registrada com sucesso!")
                        detalhes_window.destroy()
                        selecao_window.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Erro", f"Falha ao responder: {str(e)}")

            frame_botoes_detalhes = tk.Frame(detalhes_window)
            frame_botoes_detalhes.pack(pady=10)

            tk.Button(frame_botoes_detalhes, text="Salvar", command=salvar_resposta, width=15).pack(side='left', padx=5)
            tk.Button(frame_botoes_detalhes, text="Cancelar", command=detalhes_window.destroy, width=15).pack(side='left', padx=5)

        tk.Button(
            frame_botoes,
            text="Selecionar",
            command=confirmar_reclamacao,
            width=15
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes,
            text="Cancelar",
            command=selecao_window.destroy,
            width=15
        ).pack(side='left', padx=5)

            

    def menu_cliente(self, usuario):
        self.cliente_window = tk.Tk()
        self.cliente_window.title(f"Painel do Cliente - {usuario['nome']}")
        self.cliente_window.state("zoomed")

        
        frame_top = tk.Frame(self.cliente_window)
        frame_top.pack(pady=20)
        tk.Label(
            frame_top, 
            text=f"Bem-vindo(a), {usuario['nome']}", 
            font=('Arial', 14, 'bold')
        ).pack()


        frame_principal = tk.Frame(self.cliente_window)
        frame_principal.pack(pady=30)

        tk.Button(
            frame_principal, 
            text="Registrar Nova Reclamação", 
            command=lambda: self.registrar_reclamacao(usuario),
            width=25,
            height=3
        ).pack(pady=10)

        tk.Button(
            frame_principal, 
            text="Visualizar Minhas Reclamações", 
            command=lambda: self.ver_reclamacoes_cliente(usuario),
            width=25,
            height=3
        ).pack(pady=10)

        tk.Button(
            frame_principal, 
            text="Sair", 
            command=self.cliente_window.destroy,
            width=25,
            height=3
        ).pack(pady=10)

    def registrar_reclamacao(self, usuario):
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.ID_Empresa, e.Nome_Empresa 
            FROM tb_empresa e
            ORDER BY e.Nome_Empresa
        """)
        
        empresas = cursor.fetchall()
        conn.close()

        if not empresas:
            messagebox.showerror("Erro", "Nenhuma empresa cadastrada no sistema.")
            return

       
        selecao_window = tk.Toplevel(self.cliente_window)
        selecao_window.title("Selecionar Empresa")
        selecao_window.geometry("1280x720")

        tk.Label(
            selecao_window, 
            text="Selecione a empresa:", 
            font=('Arial', 20)
        ).pack(pady=10)

        frame_lista = tk.Frame(selecao_window)
        frame_lista.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        lista_empresas = tk.Listbox(
            frame_lista, 
            yscrollcommand=scrollbar.set,
            font=('Arial', 20),
            selectbackground='#4a7abc',
            selectforeground='white'
        )
        
        for emp in empresas:
            lista_empresas.insert(tk.END, f"{emp[1]}")  
        
        lista_empresas.pack(fill='both', expand=True)
        scrollbar.config(command=lista_empresas.yview)

        
        frame_botoes = tk.Frame(selecao_window)
        frame_botoes.pack(pady=10)

        def confirmar_selecao():
            try:
                selecao = lista_empresas.get(lista_empresas.curselection())
               
                for emp in empresas:
                    if emp[1] == selecao:
                        id_empresa = emp[0]
                        break
                else:
                    messagebox.showerror("Erro", "Empresa não encontrada.")
                    return
            except:
                messagebox.showerror("Erro", "Selecione uma empresa válida.")
                return

            self.registrar_reclamacao_detalhes(usuario, id_empresa, selecao, selecao_window)

        tk.Button(
            frame_botoes, 
            text="Selecionar", 
            command=confirmar_selecao,
            width=15
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=selecao_window.destroy,
            width=15
        ).pack(side='left', padx=5)

    def registrar_reclamacao_detalhes(self, usuario, id_empresa, nome_empresa, parent_window):
        detalhes_window = tk.Toplevel(parent_window)
        detalhes_window.title(f"Reclamação para {nome_empresa}")
        detalhes_window.geometry("1280x720")

        tk.Label(
            detalhes_window, 
            text=f"Registrar reclamação para: {nome_empresa}", 
            font=('Arial', 20)
        ).pack(pady=10)

   
        frame_campos = tk.Frame(detalhes_window)
        frame_campos.pack(fill='both', expand=True, padx=20, pady=10)

       
        tk.Label(frame_campos, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        entry_titulo = tk.Entry(frame_campos, width=40)
        entry_titulo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        
        tk.Label(frame_campos, text="Descrição:").grid(row=1, column=0, padx=5, pady=5, sticky='ne')
        text_descricao = tk.Text(frame_campos, width=40, height=10)
        text_descricao.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        frame_botoes = tk.Frame(detalhes_window)
        frame_botoes.pack(pady=10)

        def salvar_reclamacao():
            titulo = entry_titulo.get().strip()
            descricao = text_descricao.get("1.0", tk.END).strip()

            if not titulo or not descricao:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                return

            conn = self.conectar_banco()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO tb_reclamacoes (
                        Titulo, 
                        Descricao, 
                        ID_Cliente, 
                        ID_Empresa,
                        Status
                    ) VALUES (?, ?, ?, ?, 'Pendente')
                """, (titulo, descricao, usuario['id'], id_empresa))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "Reclamação registrada com sucesso!")
                detalhes_window.destroy()
                parent_window.destroy()
                
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Falha ao registrar: {str(e)}")
            finally:
                conn.close()

        tk.Button(
            frame_botoes, 
            text="Salvar", 
            command=salvar_reclamacao,
            width=15
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=detalhes_window.destroy,
            width=15
        ).pack(side='left', padx=5)

    def ver_reclamacoes_cliente(self, usuario):
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ID, r.Titulo, e.Nome_Empresa, r.Status, r.Data_Criacao, 
                   r.Descricao, r.Resposta, r.Data_Resposta
            FROM tb_reclamacoes r
            JOIN tb_empresa e ON r.ID_Empresa = e.ID_Empresa
            WHERE r.ID_Cliente = ?
            ORDER BY r.Data_Criacao DESC
        """, (usuario['id'],))
        
        reclamacoes = cursor.fetchall()
        conn.close()

        reclamacoes_window = tk.Toplevel(self.cliente_window)
        reclamacoes_window.title("Minhas Reclamações")
        reclamacoes_window.state("zoomed")

        frame_tree = tk.Frame(reclamacoes_window)
        frame_tree.pack(fill='both', expand=True, padx=10, pady=10)

      
        columns = ("Título", "Empresa", "Status", "Data Criação", "Descrição", "Resposta", "Data Resposta")
        tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
        
     
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='w')
        
       
        tree.column("Descrição", width=300)
        tree.column("Resposta", width=300)
        tree.column("Título", width=150)
        tree.column("Empresa", width=150)
        tree.column("Data Criação", width=120)
        tree.column("Data Resposta", width=120)

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)

        
        for rec in reclamacoes:
            data_criacao = datetime.strptime(rec[4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            data_resposta = datetime.strptime(rec[7], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M") if rec[7] else "Não respondida"
            
            tree.insert("", "end", values=(
                 rec[1], rec[2], rec[3], 
                data_criacao, rec[5], 
                rec[6] or "Sem resposta", 
                data_resposta
            ))

if __name__ == "__main__":
    app = SistemaReclamacoes()