Aplicativo de Garçom por Voz (Python)

Este é um aplicativo de linha de comando simples que demonstra como usar o reconhecimento de fala (Vosk) e a classificação de intenção (BART) para criar um sistema de pedidos de garçom por voz.
Pré-requisitos

    Python 3.7+

    Bibliotecas: vosk, transformers, pyaudio

Instalação

    Clone o repositório:

    git clone https://github.com/joaophamata/VoiceFlow
    cd garcom-app

Crie um ambiente virtual Python (recomendado):
      
python3 -m venv .venv
source .venv/bin/activate

Instale as bibliotecas:
      
pip install -r requirements.txt

    Baixe o modelo de linguagem do Vosk para português:

        Vá para https://alphacephei.com/vosk/models

        Baixe o modelo "vosk-model-small-pt-0.3.zip"

        Descompacte o arquivo zip na pasta modelo/ dentro do diretório do projeto.

Utilização

    Adapte o arquivo cardapio.py com os itens do seu cardápio.

    Execute o script:
          
    python speech_recognition.py

    Fale seu pedido no microfone quando solicitado. O aplicativo irá:

        Transcrever o áudio usando o Vosk.

        Classificar a intenção do pedido (adicionar, remover, modificar).

        Extrair entidades relevantes (item, quantidade, etc.).

    O aplicativo exibirá a transcrição, intenção detectada e entidades extraídas.

Observações

    O modelo de classificação de intenção (BART) usado neste exemplo é grande e pode ser lento em algumas máquinas. Considere usar um modelo menor se necessário.

    A extração de entidades é um processo complexo e este exemplo usa um método simples que pode não ser muito preciso.

    Este é apenas um exemplo básico e você pode precisar expandi-lo e adaptá-lo de acordo com suas necessidades.

Próximos Passos

    Melhorar a extração de entidades usando técnicas mais avançadas de PNL (NER).

    Criar uma interface gráfica para o usuário.

    Integrar com um sistema de ponto de venda (POS).

Execução do Aplicativo

    Certifique-se de ter instalado as bibliotecas necessárias.

    Baixe o modelo do Vosk e coloque-o na pasta modelo/.

    Adapte o cardapio.py com seus dados.

    Execute o script speech_recognition.py.
