#!/usr/bin/env python3
"""
ElectretPinkNoiser_GUI - Interface graphique unifiée pour le protocole de test de capsules
Gère le générateur de bruit rose et l'analyse comparative des capsules
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import io
import datetime

# Import des modules existants
try:
    from pinknoise_generator import (
        generate_pink_noise, 
        generate_pink_noise_voss, 
        save_wav
    )
    from analyze_capsules import load_and_analyze, compare_capsules
    MODULES_OK = True
except ImportError as e:
    MODULES_OK = False
    IMPORT_ERROR = str(e)


# ============================================================================
# THÈME
# ============================================================================
COLORS = {
    'bg_dark': '#0a0e1a',
    'bg_card': '#141a2e',
    'bg_card_hover': '#1a2240',
    'accent': '#00d9ff',
    'accent_2': '#00ff88',
    'accent_3': '#ff6b9d',
    'text': '#e4e9f2',
    'text_dim': '#8892b0',
    'border': '#233056',
    'error': '#ff6b6b',
    'warning': '#ffaa00',
}


# ============================================================================
# REDIRECTION DE STDOUT VERS LA ZONE DE LOG
# ============================================================================
class TextWidgetLogger:
    """Redirige stdout vers un widget Text Tkinter"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, message):
        if message.strip():
            self.text_widget.after(0, self._append, message)
    
    def _append(self, message):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, message + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')
    
    def flush(self):
        pass


# ============================================================================
# FENÊTRE PRINCIPALE
# ============================================================================
class LaboGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ElectretPinkNoiser_GUI - Interface des deux scripts")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Variables Tkinter
        self.setup_variables()
        
        # Configuration du style
        self.setup_styles()
        
        # Construction de l'interface
        self.build_ui()
        
        # Vérification des modules
        if not MODULES_OK:
            self.log(f"❌ Erreur d'import : {IMPORT_ERROR}", 'error')
            self.log("Assurez-vous que pinknoise_generator.py et analyze_capsules.py sont dans le même dossier.", 'warning')
        else:
            self.log("✅ Modules chargés avec succès", 'success')
            self.log("Bienvenue dans ElectretPinkNoiser_GUI - Interface de test de capsules électret", 'info')
    
    # ------------------------------------------------------------------------
    # VARIABLES
    # ------------------------------------------------------------------------
    def setup_variables(self):
        # Générateur
        self.gen_duration = tk.DoubleVar(value=10.0)
        self.gen_rate = tk.StringVar(value="44100")
        self.gen_bits = tk.StringVar(value="16")
        self.gen_algorithm = tk.StringVar(value="iir")
        self.gen_output = tk.StringVar(value="pink_noise.wav")
        
        # Analyseur
        self.ana_input_dir = tk.StringVar(value=".")
        self.ana_pattern = tk.StringVar(value="*.wav")
        self.ana_output = tk.StringVar(value="rapport.pdf")
        self.ana_threshold = tk.DoubleVar(value=6.0)
    
    # ------------------------------------------------------------------------
    # STYLES
    # ------------------------------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs globales
        style.configure('.', 
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text'],
                       fieldbackground=COLORS['bg_card'],
                       bordercolor=COLORS['border'],
                       darkcolor=COLORS['border'],
                       lightcolor=COLORS['border'],
                       troughcolor=COLORS['bg_dark'],
                       selectbackground=COLORS['accent'],
                       selectforeground=COLORS['bg_dark'])
        
        # Notebook (onglets)
        style.configure('TNotebook', background=COLORS['bg_dark'], borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_dim'],
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', COLORS['accent'])],
                 foreground=[('selected', COLORS['bg_dark'])])
        
        # Frames
        style.configure('Card.TFrame', background=COLORS['bg_card'])
        style.configure('Dark.TFrame', background=COLORS['bg_dark'])
        
        # Labels
        style.configure('TLabel', 
                       background=COLORS['bg_card'],
                       foreground=COLORS['text'],
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel',
                       background=COLORS['bg_dark'],
                       foreground=COLORS['accent'],
                       font=('Segoe UI', 14, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text_dim'],
                       font=('Segoe UI', 9))
        
        # Buttons
        style.configure('Accent.TButton',
                       background=COLORS['accent'],
                       foreground=COLORS['bg_dark'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.map('Accent.TButton',
                 background=[('active', COLORS['accent_2'])])
        
        style.configure('Secondary.TButton',
                       background=COLORS['bg_card'],
                       foreground=COLORS['accent'],
                       font=('Segoe UI', 10),
                       padding=8,
                       bordercolor=COLORS['accent'],
                       borderwidth=1)
        
        # Entry
        style.configure('TEntry',
                       fieldbackground=COLORS['bg_dark'],
                       foreground=COLORS['text'],
                       insertcolor=COLORS['text'])
        
        # Combobox
        style.configure('TCombobox',
                       fieldbackground=COLORS['bg_dark'],
                       foreground=COLORS['text'],
                       selectbackground=COLORS['accent'])
    
    # ------------------------------------------------------------------------
    # INTERFACE
    # ------------------------------------------------------------------------
    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['bg_dark'], pady=10)
        header.pack(fill='x', padx=20)
        
        tk.Label(header, 
                text="ElectretPinkNoiser_GUI",
                bg=COLORS['bg_dark'],
                fg=COLORS['accent'],
                font=('Segoe UI', 20, 'bold')).pack(side='left')
        
        tk.Label(header,
                bg=COLORS['bg_dark'],
                fg=COLORS['text_dim'],
                font=('Segoe UI', 9)).pack(side='left', padx=15, pady=8)
        
        # Badge IA
        badge = tk.Label(header,
                        text="🤖 100% AI Generated ✨",
                        bg=COLORS['bg_card'],
                        fg=COLORS['accent'],
                        font=('Segoe UI', 9, 'bold'),
                        padx=12, pady=4,
                        relief='solid', bd=1)
        badge.pack(side='right')
        
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Onglet 1 : Générateur
        self.tab_generator = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.tab_generator, text=' 🎵 Générateur Bruit Rose ')
        self.build_generator_tab()
        
        # Onglet 2 : Analyseur
        self.tab_analyzer = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.tab_analyzer, text=' 📊 Analyse Capsules ')
        self.build_analyzer_tab()
        
        # Zone de log (commune)
        self.build_log_area()
        
        # Footer
        footer = tk.Frame(self.root, bg=COLORS['bg_dark'], pady=5)
        footer.pack(fill='x', padx=20)
        tk.Label(footer,
                text="Fait avec ♥ pour les makers audio",
                bg=COLORS['bg_dark'],
                fg=COLORS['text_dim'],
                font=('Segoe UI', 8)).pack()
    
    # ------------------------------------------------------------------------
    # ONGLET GÉNÉRATEUR
    # ------------------------------------------------------------------------
    def build_generator_tab(self):
        container = tk.Frame(self.tab_generator, bg=COLORS['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Titre
        tk.Label(container,
                text="🌸 Générateur de Bruit Rose",
                bg=COLORS['bg_dark'],
                fg=COLORS['accent_2'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 10))
        
        tk.Label(container,
                text="Génère un fichier WAV de bruit rose pour tester vos capsules",
                bg=COLORS['bg_dark'],
                fg=COLORS['text_dim'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 20))
        
        # Card principale
        card = tk.Frame(container, bg=COLORS['bg_card'], 
                       highlightbackground=COLORS['border'],
                       highlightthickness=1, padx=20, pady=20)
        card.pack(fill='x')
        
        # Grid pour les paramètres
        params = tk.Frame(card, bg=COLORS['bg_card'])
        params.pack(fill='x')
        
        # Durée
        tk.Label(params, text="Durée (s) :", bg=COLORS['bg_card'], 
                fg=COLORS['text']).grid(row=0, column=0, sticky='w', pady=8, padx=(0, 10))
        tk.Spinbox(params, from_=1.0, to=300.0, increment=1.0,
                  textvariable=self.gen_duration, width=15,
                  bg=COLORS['bg_dark'], fg=COLORS['text'],
                  buttonbackground=COLORS['bg_card']).grid(row=0, column=1, sticky='w', pady=8)
        
        # Fréquence d'échantillonnage
        tk.Label(params, text="Fréquence (Hz) :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=1, column=0, sticky='w', pady=8, padx=(0, 10))
        ttk.Combobox(params, textvariable=self.gen_rate, width=13,
                    values=['22050', '44100', '48000', '96000'],
                    state='readonly').grid(row=1, column=1, sticky='w', pady=8)
        
        # Profondeur
        tk.Label(params, text="Profondeur (bits) :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=2, column=0, sticky='w', pady=8, padx=(0, 10))
        ttk.Combobox(params, textvariable=self.gen_bits, width=13,
                    values=['16', '24'], state='readonly').grid(row=2, column=1, sticky='w', pady=8)
        
        # Algorithme
        tk.Label(params, text="Algorithme :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=3, column=0, sticky='w', pady=8, padx=(0, 10))
        algo_frame = tk.Frame(params, bg=COLORS['bg_card'])
        algo_frame.grid(row=3, column=1, sticky='w', pady=8)
        tk.Radiobutton(algo_frame, text="IIR (rapide)", variable=self.gen_algorithm,
                      value="iir", bg=COLORS['bg_card'], fg=COLORS['text'],
                      selectcolor=COLORS['bg_dark'], activebackground=COLORS['bg_card'],
                      activeforeground=COLORS['accent']).pack(side='left', padx=(0, 15))
        tk.Radiobutton(algo_frame, text="Voss-McCartney (précis)", variable=self.gen_algorithm,
                      value="voss", bg=COLORS['bg_card'], fg=COLORS['text'],
                      selectcolor=COLORS['bg_dark'], activebackground=COLORS['bg_card'],
                      activeforeground=COLORS['accent']).pack(side='left')
        
        # Fichier de sortie
        tk.Label(params, text="Fichier de sortie :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=4, column=0, sticky='w', pady=8, padx=(0, 10))
        out_frame = tk.Frame(params, bg=COLORS['bg_card'])
        out_frame.grid(row=4, column=1, sticky='ew', pady=8)
        tk.Entry(out_frame, textvariable=self.gen_output, width=30,
                bg=COLORS['bg_dark'], fg=COLORS['text'],
                insertbackground=COLORS['text']).pack(side='left', padx=(0, 5))
        ttk.Button(out_frame, text="Parcourir...", 
                  command=self.browse_output_wav).pack(side='left')
        
        params.columnconfigure(1, weight=1)
        
        # Bouton Générer
        btn_frame = tk.Frame(card, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame, text="🎵 Générer le bruit rose",
                  style='Accent.TButton',
                  command=self.run_generate).pack(side='left')
        
        ttk.Button(btn_frame, text="🔄 Réinitialiser",
                  style='Secondary.TButton',
                  command=self.reset_generator).pack(side='left', padx=10)
    
    # ------------------------------------------------------------------------
    # ONGLET ANALYSEUR
    # ------------------------------------------------------------------------
    def build_analyzer_tab(self):
        container = tk.Frame(self.tab_analyzer, bg=COLORS['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Titre
        tk.Label(container,
                text="📊 Analyse Comparative des Capsules",
                bg=COLORS['bg_dark'],
                fg=COLORS['accent_2'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 10))
        
        tk.Label(container,
                text="Compare les enregistrements et génère un rapport PDF",
                bg=COLORS['bg_dark'],
                fg=COLORS['text_dim'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 20))
        
        # Card principale
        card = tk.Frame(container, bg=COLORS['bg_card'],
                       highlightbackground=COLORS['border'],
                       highlightthickness=1, padx=20, pady=20)
        card.pack(fill='x')
        
        # Grid pour les paramètres
        params = tk.Frame(card, bg=COLORS['bg_card'])
        params.pack(fill='x')
        
        # Dossier d'entrée
        tk.Label(params, text="Dossier d'entrée :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=0, column=0, sticky='w', pady=8, padx=(0, 10))
        in_frame = tk.Frame(params, bg=COLORS['bg_card'])
        in_frame.grid(row=0, column=1, sticky='ew', pady=8)
        tk.Entry(in_frame, textvariable=self.ana_input_dir, width=30,
                bg=COLORS['bg_dark'], fg=COLORS['text'],
                insertbackground=COLORS['text']).pack(side='left', padx=(0, 5))
        ttk.Button(in_frame, text="Parcourir...",
                  command=self.browse_input_dir).pack(side='left')
        
        # Motif
        tk.Label(params, text="Motif de fichier :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=1, column=0, sticky='w', pady=8, padx=(0, 10))
        tk.Entry(params, textvariable=self.ana_pattern, width=35,
                bg=COLORS['bg_dark'], fg=COLORS['text'],
                insertbackground=COLORS['text']).grid(row=1, column=1, sticky='w', pady=8)
        
        # Rapport PDF
        tk.Label(params, text="Rapport PDF :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=2, column=0, sticky='w', pady=8, padx=(0, 10))
        out_frame = tk.Frame(params, bg=COLORS['bg_card'])
        out_frame.grid(row=2, column=1, sticky='ew', pady=8)
        tk.Entry(out_frame, textvariable=self.ana_output, width=30,
                bg=COLORS['bg_dark'], fg=COLORS['text'],
                insertbackground=COLORS['text']).pack(side='left', padx=(0, 5))
        ttk.Button(out_frame, text="Parcourir...",
                  command=self.browse_output_pdf).pack(side='left')
        
        # Seuil
        tk.Label(params, text="Seuil de rejet (dB) :", bg=COLORS['bg_card'],
                fg=COLORS['text']).grid(row=3, column=0, sticky='w', pady=8, padx=(0, 10))
        tk.Spinbox(params, from_=1.0, to=20.0, increment=0.5,
                  textvariable=self.ana_threshold, width=15,
                  bg=COLORS['bg_dark'], fg=COLORS['text'],
                  buttonbackground=COLORS['bg_card']).grid(row=3, column=1, sticky='w', pady=8)
        
        params.columnconfigure(1, weight=1)
        
        # Bouton Analyser
        btn_frame = tk.Frame(card, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame, text="📊 Analyser les capsules",
                  style='Accent.TButton',
                  command=self.run_analyze).pack(side='left')
        
        ttk.Button(btn_frame, text="📂 Ouvrir le rapport",
                  style='Secondary.TButton',
                  command=self.open_report).pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="🔄 Réinitialiser",
                  style='Secondary.TButton',
                  command=self.reset_analyzer).pack(side='left')
    
    # ------------------------------------------------------------------------
    # ZONE DE LOG
    # ------------------------------------------------------------------------
    def build_log_area(self):
        log_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        tk.Label(log_frame,
                text="📋 Console",
                bg=COLORS['bg_dark'],
                fg=COLORS['accent'],
                font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg=COLORS['bg_dark'],
            fg=COLORS['text'],
            font=('Consolas', 9),
            insertbackground=COLORS['text'],
            relief='solid',
            bd=1,
            highlightbackground=COLORS['border'],
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True)
        self.log_text.configure(state='disabled')
        
        # Configuration des tags pour colorer les logs
        self.log_text.tag_configure('info', foreground=COLORS['text'])
        self.log_text.tag_configure('success', foreground=COLORS['accent_2'])
        self.log_text.tag_configure('warning', foreground=COLORS['warning'])
        self.log_text.tag_configure('error', foreground=COLORS['error'])
        self.log_text.tag_configure('title', foreground=COLORS['accent'], font=('Consolas', 10, 'bold'))
        
        # Bouton effacer
        clear_btn = tk.Button(log_frame,
                            text="🗑️ Effacer la console",
                            bg=COLORS['bg_card'],
                            fg=COLORS['text_dim'],
                            relief='flat',
                            font=('Segoe UI', 9),
                            command=self.clear_log,
                            cursor='hand2')
        clear_btn.pack(anchor='e', pady=(5, 0))
    
    # ------------------------------------------------------------------------
    # MÉTHODES UTILITAIRES
    # ------------------------------------------------------------------------
    def log(self, message, level='info'):
        """Ajoute un message à la zone de log"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        formatted = f"[{timestamp}] {message}"
        
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, formatted + '\n', level)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
    
    def clear_log(self):
        """Efface la zone de log"""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
    
    def browse_output_wav(self):
        """Sélection du fichier WAV de sortie"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile=self.gen_output.get()
        )
        if filename:
            self.gen_output.set(filename)
    
    def browse_input_dir(self):
        """Sélection du dossier d'entrée"""
        dirname = filedialog.askdirectory(initialdir=self.ana_input_dir.get())
        if dirname:
            self.ana_input_dir.set(dirname)
    
    def browse_output_pdf(self):
        """Sélection du fichier PDF de sortie"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=self.ana_output.get()
        )
        if filename:
            self.ana_output.set(filename)
    
    def reset_generator(self):
        """Réinitialise les paramètres du générateur"""
        self.gen_duration.set(10.0)
        self.gen_rate.set("44100")
        self.gen_bits.set("16")
        self.gen_algorithm.set("iir")
        self.gen_output.set("pink_noise.wav")
        self.log("Paramètres du générateur réinitialisés", 'info')
    
    def reset_analyzer(self):
        """Réinitialise les paramètres de l'analyseur"""
        self.ana_input_dir.set(".")
        self.ana_pattern.set("*.wav")
        self.ana_output.set("rapport.pdf")
        self.ana_threshold.set(6.0)
        self.log("Paramètres de l'analyseur réinitialisés", 'info')
    
    def open_report(self):
        """Ouvre le rapport PDF généré"""
        pdf_path = self.ana_output.get()
        if not os.path.exists(pdf_path):
            messagebox.showwarning("Fichier introuvable",
                                 f"Le fichier {pdf_path} n'existe pas encore.\nLancez d'abord une analyse.")
            return
        
        # Tente d'ouvrir avec le viewer par défaut
        import subprocess
        import platform
        try:
            if platform.system() == 'Darwin':
                subprocess.call(('open', pdf_path))
            elif platform.system() == 'Windows':
                os.startfile(pdf_path)
            else:
                subprocess.call(('xdg-open', pdf_path))
            self.log(f"📂 Ouverture du rapport : {pdf_path}", 'success')
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")
    
    # ------------------------------------------------------------------------
    # EXÉCUTION DES TÂCHES (THREADING)
    # ------------------------------------------------------------------------
    def run_generate(self):
        """Lance la génération dans un thread séparé"""
        if not MODULES_OK:
            messagebox.showerror("Erreur", "Modules non chargés. Vérifiez les fichiers Python.")
            return
        
        self.log("=" * 50, 'title')
        self.log("🎵 LANCEMENT DE LA GÉNÉRATION", 'title')
        self.log(f"   Durée : {self.gen_duration.get()} s", 'info')
        self.log(f"   Fréquence : {self.gen_rate.get()} Hz", 'info')
        self.log(f"   Profondeur : {self.gen_bits.get()} bits", 'info')
        self.log(f"   Algorithme : {self.gen_algorithm.get()}", 'info')
        self.log(f"   Fichier : {self.gen_output.get()}", 'info')
        
        def task():
            try:
                # Redirection stdout
                old_stdout = sys.stdout
                sys.stdout = TextWidgetLogger(self.log_text)
                
                duration = self.gen_duration.get()
                rate = int(self.gen_rate.get())
                bits = int(self.gen_bits.get())
                output = self.gen_output.get()
                algorithm = self.gen_algorithm.get()
                
                n_samples = int(duration * rate)
                
                if algorithm == 'voss':
                    pink_noise = generate_pink_noise_voss(n_samples)
                else:
                    pink_noise = generate_pink_noise(duration, rate)
                
                save_wav(output, pink_noise, rate, bits)
                
                sys.stdout = old_stdout
                self.log("✅ Génération terminée avec succès !", 'success')
                
            except Exception as e:
                sys.stdout = sys.__stdout__
                self.log(f"❌ Erreur lors de la génération : {e}", 'error')
                import traceback
                self.log(traceback.format_exc(), 'error')
        
        threading.Thread(target=task, daemon=True).start()
    
    def run_analyze(self):
        """Lance l'analyse dans un thread séparé"""
        if not MODULES_OK:
            messagebox.showerror("Erreur", "Modules non chargés. Vérifiez les fichiers Python.")
            return
        
        input_dir = self.ana_input_dir.get()
        if not os.path.isdir(input_dir):
            messagebox.showerror("Erreur", f"Le dossier {input_dir} n'existe pas.")
            return
        
        self.log("=" * 50, 'title')
        self.log("📊 LANCEMENT DE L'ANALYSE", 'title')
        self.log(f"   Dossier : {input_dir}", 'info')
        self.log(f"   Motif : {self.ana_pattern.get()}", 'info')
        self.log(f"   Rapport : {self.ana_output.get()}", 'info')
        self.log(f"   Seuil : ±{self.ana_threshold.get()} dB", 'info')
        
        def task():
            try:
                old_stdout = sys.stdout
                sys.stdout = TextWidgetLogger(self.log_text)
                
                import glob
                search_pattern = os.path.join(input_dir, self.ana_pattern.get())
                wav_files = sorted(glob.glob(search_pattern))
                
                if not wav_files:
                    self.log(f"❌ Aucun fichier WAV trouvé avec le motif {self.ana_pattern.get()}", 'error')
                    sys.stdout = old_stdout
                    return
                
                self.log(f"🔍 {len(wav_files)} fichier(s) WAV trouvé(s)", 'info')
                
                results = []
                for wav_file in wav_files:
                    self.log(f"   Analyse : {os.path.basename(wav_file)}...", 'info')
                    result = load_and_analyze(wav_file)
                    results.append(result)
                    self.log(f"      ✅ {result['duration']:.1f}s, {result['rms_db']:.1f} dB", 'success')
                
                if len(results) < 2:
                    self.log("⚠️ Il faut au moins 2 fichiers valides pour une comparaison", 'warning')
                    sys.stdout = old_stdout
                    return
                
                compare_capsules(results, self.ana_output.get())
                
                sys.stdout = old_stdout
                self.log("=" * 50, 'title')
                self.log(f"✅ Rapport généré : {self.ana_output.get()}", 'success')
                
            except Exception as e:
                sys.stdout = sys.__stdout__
                self.log(f"❌ Erreur lors de l'analyse : {e}", 'error')
                import traceback
                self.log(traceback.format_exc(), 'error')
        
        threading.Thread(target=task, daemon=True).start()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================
def main():
    root = tk.Tk()
    
    try:
        root.iconbitmap(default='')
    except:
        pass
    
    app = LaboGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
