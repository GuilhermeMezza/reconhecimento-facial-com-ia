# reconhecimento-facial-com-ia

💻 Materiais Utilizados:
- Arduino Uno: Cérebro do sistema para controlar os componentes.
- Display OLED: Exibição de mensagens e instruções para o usuário.
- Teclado Matricial 4x4: Para interações e comandos, como cadastro e remoção de faces.
- Relé: Responsável por ativar a fechadura eletrônica.
- Webcam: Para captura de imagens e reconhecimento facial.

🔑 Inteligência Artificial Aplicada: O sistema de reconhecimento facial foi construído com a ajuda de bibliotecas de IA e ferramentas de visão computacional. Foi utilizado OpenCV para capturar e processar imagens da webcam e a biblioteca face_recognition para o reconhecimento facial, aproveitando seu poderoso algoritmo de detecção de rostos. O código foi desenvolvido em Python para gerenciar tanto a IA quanto a comunicação com o Arduino.

📚 Bibliotecas Usadas:
- OpenCV: Processamento de imagens, captura de vídeo e detecção de rostos em tempo real.
- face_recognition: Responsável pela identificação e verificação de rostos já cadastrados no sistema.
- os: Manipulação de diretórios e arquivos para o gerenciamento dos dados de usuários.
- serial: Comunicação com o Arduino para controlar o destravamento da fechadura.
- time: Gerenciamento de temporizações e intervalos no fluxo do sistema.
- pickle: Serialização e desserialização dos dados, permitindo salvar e carregar facilmente os rostos reconhecidos.
