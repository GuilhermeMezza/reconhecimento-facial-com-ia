 #include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Keypad.h>

// Definições para o display OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pinos dos LEDs
int ledVerde = 11;
int ledVermelho = 12;
int ledAmarelo = 13;

// Pino do relé
int rele = 10;  // Pino do relé para controle da trava

// Configuração do teclado matricial 4x4
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
  // Inicializar o display OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {  // Endereço I2C 0x3C para a maioria dos displays OLED
    Serial.println(F("Falha ao inicializar o OLED"));
    for (;;);  // Parar aqui se o display falhar
  }
  
  // Limpar o buffer de exibição
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.display();

  // Inicializar LEDs
  pinMode(ledVerde, OUTPUT);
  pinMode(ledVermelho, OUTPUT);
  pinMode(ledAmarelo, OUTPUT);
  
  // Inicializar o relé
  pinMode(rele, OUTPUT);
  digitalWrite(rele, HIGH);  // Desativar o relé inicialmente (trava fechada)

  // Iniciar comunicação Serial
  Serial.begin(9600);
}

void loop() {
  // Ler o teclado
  char key = keypad.getKey();

  // Se uma tecla for pressionada, enviar via serial
  if (key) {
    Serial.println(key);
  }

  // Verificar comandos recebidos via serial
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');

    // Controlar os LEDs
    if (comando == "LED_RED") {
      digitalWrite(ledVermelho, HIGH);
      digitalWrite(ledAmarelo, LOW);
      digitalWrite(ledVerde, LOW);
    } else if (comando == "LED_YELLOW") {
      digitalWrite(ledVermelho, LOW);
      digitalWrite(ledAmarelo, HIGH);
      digitalWrite(ledVerde, LOW);
    } else if (comando == "LED_GREEN") {
      digitalWrite(ledVermelho, LOW);
      digitalWrite(ledAmarelo, LOW);
      digitalWrite(ledVerde, HIGH);
    }

    // Controlar o relé (abrir ou fechar a trava)
    if (comando == "OPEN_LOCK") {
      digitalWrite(rele, LOW);  // Ativar o relé para abrir a trava
      delay(5000);              // Manter a trava aberta por 5 segundos
      digitalWrite(rele, HIGH); // Fechar a trava
    }

    // Atualizar display OLED
    if (comando.startsWith("DISPLAY:")) {
      String mensagem = comando.substring(8);  // Extrair a mensagem

      display.clearDisplay();
      display.setCursor(0, 0);
      display.println(mensagem);
      display.display();
    }
  }
}
