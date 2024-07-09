import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel
from transformers import pipeline
from cardapio import CARDAPIO
import tkinter as tk
from tkinter import ttk, messagebox

# --- Configurações ---
MODELO_VOSK_PATH = "models/vosk/vosk-model-small-pt-0.3"
INTENT_CLASSIFIER_NAME = "facebook/bart-large-mnli"

# --- Carregamento de Modelos ---
SetLogLevel(0)
vosk_model = Model(MODELO_VOSK_PATH)
recognizer = KaldiRecognizer(vosk_model, 16000)
intent_classifier = pipeline("zero-shot-classification", model=INTENT_CLASSIFIER_NAME)

# --- Classe Pedido ---
class Pedido:
    def __init__(self):
        self.itens = []

    def adicionar_item(self, item, quantidade):
        self.itens.append({"item": item, "quantidade": quantidade})

    def remover_item(self, item):
        for i in range(len(self.itens) - 1, -1, -1): 
            if self.itens[i]["item"] == item:
                del self.itens[i]
                break

    def exibir_pedido(self):
        if not self.itens:
            return "O pedido está vazio."
        else:
            descricao = "=== Pedido ===\n"
            for item in self.itens:
                descricao += f"{item['quantidade']}x {item['item']}\n"
            descricao += "=============="
            return descricao

# --- Funções ---
def capturar_e_transcrever_audio():
    """Captura áudio do microfone e transcreve usando o Vosk."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    texto_transcrito = ""

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Gravando...")

    while True:
        data = stream.read(CHUNK)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            texto_transcrito = result.get("text", "")
            if texto_transcrito:
                break

    print("Gravação finalizada!")
    stream.stop_stream()
    stream.close()
    p.terminate()
    return texto_transcrito


def classificar_intencao(texto):
    """Classifica a intenção usando o BART."""
    labels = ["adicionar item", "remover item", "modificar item"]
    result = intent_classifier(texto, labels)
    return result['labels'][0]

def extrair_entidades(texto):
    """Extrai entidades relevantes do texto."""
    entidades = {}
    texto = texto.lower()

    for palavra in texto.split():
        if palavra.isdigit():
            entidades["quantidade"] = int(palavra)
            break

    for categoria in CARDAPIO["categorias"]:
        for item in categoria["itens"]:
            if item["nome"].lower() in texto:
                entidades["item"] = item["nome"]
                for chave in item:
                    if chave != "nome" and isinstance(item[chave], list):
                        for valor in item[chave]:
                            if valor.lower() in texto:
                                entidades[chave] = valor
                                break

    return entidades

# --- Funções da Interface ---
def adicionar_item_interface():
    texto_item = entrada_item.get()
    quantidade = int(entrada_quantidade.get()) if entrada_quantidade.get().isdigit() else 1
    pedido_atual.adicionar_item(texto_item, quantidade)
    atualizar_listbox_pedido()
    entrada_item.delete(0, tk.END) 
    entrada_quantidade.delete(0, tk.END)

def remover_item_interface():
    try:
        selecionado = listbox_pedido.curselection()[0]
        pedido_atual.itens.pop(selecionado)
        atualizar_listbox_pedido()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione um item para remover.")

def modificar_item_interface():
    try:
        selecionado = listbox_pedido.curselection()[0]
        item_atual = pedido_atual.itens[selecionado]["item"]
        quantidade_atual = pedido_atual.itens[selecionado]["quantidade"]

        nova_janela = tk.Toplevel(janela)
        nova_janela.title("Modificar Item")

        tk.Label(nova_janela, text="Item:").grid(row=0, column=0)
        entrada_novo_item = tk.Entry(nova_janela)
        entrada_novo_item.insert(0, item_atual)
        entrada_novo_item.grid(row=0, column=1)

        tk.Label(nova_janela, text="Quantidade:").grid(row=1, column=0)
        entrada_nova_quantidade = tk.Entry(nova_janela)
        entrada_nova_quantidade.insert(0, str(quantidade_atual))
        entrada_nova_quantidade.grid(row=1, column=1)

        def salvar_modificacao():
            novo_item = entrada_novo_item.get()
            nova_quantidade = int(entrada_nova_quantidade.get()) if entrada_nova_quantidade.get().isdigit() else 1
            pedido_atual.itens[selecionado] = {"item": novo_item, "quantidade": nova_quantidade}
            atualizar_listbox_pedido()
            nova_janela.destroy()

        tk.Button(nova_janela, text="Salvar", command=salvar_modificacao).grid(row=2, column=0, columnspan=2)

    except IndexError:
        messagebox.showwarning("Aviso", "Selecione um item para modificar.")

def atualizar_listbox_pedido():
    listbox_pedido.delete(0, tk.END)
    for item in pedido_atual.itens:
        listbox_pedido.insert(tk.END, f"{item['quantidade']}x {item['item']}")

def processar_voz():
    texto_transcrito = capturar_e_transcrever_audio()
    if texto_transcrito:
        intencao = classificar_intencao(texto_transcrito)
        entidades = extrair_entidades(texto_transcrito)

        if intencao == "adicionar item" and "item" in entidades and "quantidade" in entidades:
            pedido_atual.adicionar_item(entidades["item"], entidades["quantidade"])
        elif intencao == "remover item" and "item" in entidades:
            pedido_atual.remover_item(entidades["item"])

        atualizar_listbox_pedido()
        texto_resultado.config(text=f"Transcrição: {texto_transcrito}\n"
                                    f"Intenção: {intencao}\n"
                                    f"Entidades: {entidades}")
    else:
        texto_resultado.config(text="Nenhuma transcrição detectada. Tente novamente.")

# --- Interface Gráfica ---
janela = tk.Tk()
janela.title("Sistema de Pedidos do Garçom")

pedido_atual = Pedido()

# Widgets
tk.Label(janela, text="Item:").grid(row=0, column=0)
entrada_item = tk.Entry(janela)
entrada_item.grid(row=0, column=1)

tk.Label(janela, text="Quantidade:").grid(row=1, column=0)
entrada_quantidade = tk.Entry(janela)
entrada_quantidade.grid(row=1, column=1)

botao_adicionar = tk.Button(janela, text="Adicionar", command=adicionar_item_interface)
botao_adicionar.grid(row=0, column=2)
botao_remover = tk.Button(janela, text="Remover", command=remover_item_interface)
botao_remover.grid(row=1, column=2)
botao_modificar = tk.Button(janela, text="Modificar", command=modificar_item_interface)
botao_modificar.grid(row=1, column=3)

botao_voz = tk.Button(janela, text="Falar Pedido", command=processar_voz)
botao_voz.grid(row=2, column=0, columnspan=2)

listbox_pedido = tk.Listbox(janela)
listbox_pedido.grid(row=3, column=0, columnspan=3)

texto_resultado = tk.Label(janela, text="")
texto_resultado.grid(row=4, column=0, columnspan=3)

janela.mainloop()