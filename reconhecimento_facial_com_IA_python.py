import cv2
import face_recognition
import os
import serial
import time
import pickle

# Configuração da comunicação serial com o Arduino (ajuste a porta serial conforme necessário)
arduino = serial.Serial('COM3', 9600, timeout=1)  # Altere 'COM3' pela porta do seu Arduino
time.sleep(2)  # Aguarde para garantir que a conexão seja estabelecida

# Senha de administrador
ADMIN_PASSWORD = "1234"

# Caminho para o cache de encodings
ENCODING_CACHE_FILE = './encoding_cache.pickle'

# Carregar as imagens uma vez no início do programa
imagens_cadastradas, ids_cadastrados = [], []

def carregar_encodings_cache():
    """Carregar encodings do cache, se existir"""
    global imagens_cadastradas, ids_cadastrados
    if os.path.exists(ENCODING_CACHE_FILE):
        with open(ENCODING_CACHE_FILE, 'rb') as file:
            cache = pickle.load(file)
            imagens_cadastradas = cache['encodings']
            ids_cadastrados = cache['ids']
            print(f"{len(ids_cadastrados)} faces carregadas do cache.")

def salvar_encodings_cache():
    """Salvar encodings no cache"""
    with open(ENCODING_CACHE_FILE, 'wb') as file:
        pickle.dump({'encodings': imagens_cadastradas, 'ids': ids_cadastrados}, file)

def carregar_imagens_cadastradas():
    """Função para carregar imagens cadastradas e extrair os encodings faciais"""
    global imagens_cadastradas, ids_cadastrados
    path = './imagens_cadastradas'
    lista_arquivos = os.listdir(path)

    for arquivo in lista_arquivos:
        img = cv2.imread(f'{path}/{arquivo}')
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if len(encodings) > 0:
            encoding = encodings[0]
            imagens_cadastradas.append(encoding)
            ids_cadastrados.append(os.path.splitext(arquivo)[0])  # ID do arquivo
    salvar_encodings_cache()

# Tenta carregar encodings do cache
carregar_encodings_cache()

def controlar_led(led_cor):
    """Função para controlar os LEDs"""
    if led_cor == 'vermelho':
        arduino.write(b'LED_RED\n')
    elif led_cor == 'amarelo':
        arduino.write(b'LED_YELLOW\n')
    elif led_cor == 'verde':
        arduino.write(b'LED_GREEN\n')

def atualizar_lcd(mensagem):
    """Função para atualizar o display LCD"""
    arduino.write(f'DISPLAY:{mensagem}\n'.encode())

def ler_teclado():
    """Função para ler a tecla do teclado matricial"""
    arduino.write(b'READ_KEYPAD\n')  # Enviar comando para ler a tecla
    tecla = arduino.readline().decode().strip()
    return tecla

def solicitar_senha():
    """Função para solicitar senha"""
    senha_digitada = ""
    atualizar_lcd("Digite a senha: ")
    print("Digite a senha: ")
    while True:
        tecla = ler_teclado()
        if tecla == '#':  # Confirmação da senha
            break
        elif tecla.isdigit():  # Adicionar dígito à senha
            senha_digitada += tecla
            print("*", end="", flush=True)  # Mostrar '*' na tela
    print()  # Nova linha após a senha
    return senha_digitada

def cadastrar_nova_face():
    """Função para cadastrar nova face"""
    senha = solicitar_senha()
    if senha == ADMIN_PASSWORD:
        atualizar_lcd("Senha correta!")
        print("Senha correta! Capturando nova face...")
        
        # Iniciar processamento
        controlar_led('amarelo')
        
        # Iniciar webcam
        '''cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            controlar_led('vermelho')
            atualizar_lcd("Erro webcam!")
            print("Erro ao acessar a webcam")
            return'''
        
        # Capturar imagem
        ret, frame = cap.read()
        if not ret:
            controlar_led('vermelho')
            atualizar_lcd("Erro captura!")
            print("Erro ao capturar imagem da webcam")
            return
        
        # Reduzir a resolução da imagem para aumentar a velocidade
        frame_pequeno = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Converter a imagem capturada para RGB
        img_rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

        # Obter o encoding da face
        encodings = face_recognition.face_encodings(img_rgb)
        if len(encodings) > 0:
            encoding = encodings[0]

            # Salvar imagem com novo ID
            path = './imagens_cadastradas'
            novo_id = str(len(os.listdir(path)) + 1)  # Novo ID numérico crescente
            cv2.imwrite(f'{path}/{novo_id}.jpg', frame)  # Salvar a imagem original
            
            # Atualizar listas de imagens e encodings
            imagens_cadastradas.append(encoding)
            ids_cadastrados.append(novo_id)
            salvar_encodings_cache()

            controlar_led('verde')
            atualizar_lcd(f"Face cadastrada! ID: {novo_id}")
            print(f"Face cadastrada com sucesso! ID: {novo_id}")
        else:
            controlar_led('vermelho')
            atualizar_lcd("Nenhuma face detectada")
            print("Nenhuma face detectada")

        #cap.release()
    else:
        controlar_led('vermelho')
        atualizar_lcd("Senha incorreta!")
        print("Senha incorreta. Acesso negado.")

def apagar_face():
    """Função para apagar face cadastrada"""
    senha = solicitar_senha()
    if senha == ADMIN_PASSWORD:
        atualizar_lcd("Senha correta!")
        print("Senha correta!")
        
        # Solicitar ID da face a ser apagada
        atualizar_lcd("Digite ID a apagar:")
        print("Digite o ID da face a ser apagada: ")
        face_id = ""
        while True:
            tecla = ler_teclado()
            if tecla == '#':  # Confirmação do ID
                break
            elif tecla.isdigit():  # Adicionar dígito ao ID
                face_id += tecla
                print(tecla, end="", flush=True)
        print()  # Nova linha após o ID
        
        # Apagar o arquivo correspondente
        path = f'./imagens_cadastradas/{face_id}.jpg'
        if os.path.exists(path):
            os.remove(path)
            # Remover o ID e encoding da lista
            if face_id in ids_cadastrados:
                index = ids_cadastrados.index(face_id)
                del ids_cadastrados[index]
                del imagens_cadastradas[index]
                salvar_encodings_cache()
            
            controlar_led('verde')
            atualizar_lcd(f"Face {face_id} apagada")
            print(f"Face com ID {face_id} apagada com sucesso.")
        else:
            controlar_led('vermelho')
            atualizar_lcd(f"ID {face_id} não encontrado")
            print(f"ID {face_id} não encontrado.")
    else:
        controlar_led('vermelho')
        atualizar_lcd("Senha incorreta!")
        print("Senha incorreta. Acesso negado.")

def abrir_trava():
    """Função para abrir a trava"""
    arduino.write(b'OPEN_LOCK\n')
    controlar_led('verde')
    atualizar_lcd("Trava aberta!")
    print("Trava aberta!")

def reconhecimento_facial():
    """Função principal para reconhecimento facial"""
    # Iniciar webcam
    '''cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        controlar_led('vermelho')
        atualizar_lcd("Erro webcam!")
        print("Erro ao acessar a webcam")
        return'''

    atualizar_lcd("Reconhecendo face...")
    print("Capturando imagem para reconhecimento facial...")

    # Iniciar processamento
    controlar_led('amarelo')

    ret, frame = cap.read()
    if not ret:
        controlar_led('vermelho')
        atualizar_lcd("Erro captura!")
        print("Erro ao capturar imagem da webcam")
        return

    # Reduzir a resolução da imagem para aumentar a velocidade
    frame_pequeno = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Converter a imagem capturada para RGB
    frame_rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

    # Detectar rostos na imagem usando HOG (mais rápido)
    face_locations = face_recognition.face_locations(frame_rgb, model="hog")
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

    # Verificar se algum rosto foi encontrado
    if face_encodings:
        for face_encoding in face_encodings:
            # Comparar rostos encontrados com os rostos cadastrados
            resultados = face_recognition.compare_faces(imagens_cadastradas, face_encoding)
            distancias = face_recognition.face_distance(imagens_cadastradas, face_encoding)
            melhor_match = resultados.index(True) if True in resultados else None

            if melhor_match is not None and distancias[melhor_match] < 0.6:  # Ajuste do nível de tolerância
                id_reconhecido = ids_cadastrados[melhor_match]
                controlar_led('verde')
                atualizar_lcd(f"Rosto reconhecido: ID {id_reconhecido}")
                print(f"Rosto reconhecido. ID: {id_reconhecido}")
                abrir_trava()
            else:
                controlar_led('vermelho')
                atualizar_lcd("Rosto não reconhecido")
                print("Rosto não reconhecido")
    else:
        controlar_led('vermelho')
        atualizar_lcd("Nenhum rosto encontrado")
        print("Nenhum rosto encontrado")

    #cap.release()

def limpar_cache():
    """Função para limpar o cache de encodings"""
    senha = solicitar_senha()
    if senha == ADMIN_PASSWORD:
        global imagens_cadastradas, ids_cadastrados
        if os.path.exists(ENCODING_CACHE_FILE):
            os.remove(ENCODING_CACHE_FILE)
            imagens_cadastradas = []
            ids_cadastrados = []
            controlar_led('verde')
            atualizar_lcd("Cache limpo!")
            print("Cache de encodings foi limpo.")
        else:
            controlar_led('amarelo')
            atualizar_lcd("Cache já está vazio.")
            print("Cache já estava vazio.")
    else:
        controlar_led('vermelho')
        atualizar_lcd("Senha incorreta!")
        print("Senha incorreta. Acesso negado.")

if __name__ == "__main__":
    try:
        cap = cv2.VideoCapture(0)  # Altere para '0' ou '1' dependendo da câmera desejada
        if not cap.isOpened():
            print("Erro ao acessar a câmera")
            exit()
        while True:
            atualizar_lcd("Menu: A-Ler B-Cad C-Del D-Limpar")
            print("Pressione 'A' para reconhecimento facial, 'B' para cadastrar uma nova face, 'C' para apagar uma face, ou 'D' para limpar o cache.")
            tecla = ler_teclado()

            if tecla == 'A':
                reconhecimento_facial()
            elif tecla == 'B':
                cadastrar_nova_face()
            elif tecla == 'C':
                apagar_face()
            elif tecla == 'D':
                limpar_cache()
    except KeyboardInterrupt:
        print("Programa encerrado.")
    finally:
        if arduino.is_open:
            arduino.close()

