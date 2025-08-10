# define BLYNK_TEMPLATE_NAME "DHT and Button"

from machine import Pin, Timer
from BlynkLib import Blynk
from network import WLAN, STA_IF
import dht
from time import sleep_ms

sensor = dht.DHT11(Pin(4))		# Define o sensor DHT11 no pino 4
relay = Pin(2, Pin.OUT)			# Define o pino do ESP32 onde o relé está ligado (GPIO2)
relay.value(0)					# Inicia com rele desligado (FAN OFF)

# WiFi settings e BLYNK token config
# SSID = "SOULARGO"
# PASS = "soulargo24"
SSID = "rede_pesca"
PASS = "fr33debi"

BLYNK_AUTH_TOKEN = "WLtNFMUMY3TrhNk_lShbBNQ8M3mogtuu"

modo_manual = False  # False = automático pela temperatura, True = manual


# **************************
# Função que estabelece ligação com a rede WiFi
# **************************
def conn():    
    interface = WLAN(STA_IF)
    interface.active(True)
    interface.connect(SSID, PASS)
    max_secs = 20
    print("Connecting: ", end="")

    while not interface.isconnected() and max_secs > 0:
        print(".", end="")
        sleep_ms(1000)
        max_secs -= 1

    if max_secs == 0:
        print("\nCouldn't connect to network!!!")
    else:
        print("\nNow connected to the wireless network!")
        ip_addr, mask, gateway, dns_srv = interface.ifconfig()
        print("IP address: ", ip_addr)
        print("Network mask: ", mask)
        print("Gateway: ", gateway)
        print("DNS server: ", dns_srv)
        print("*******************")
        
        
# **************************
# Função leitura sensor DHT
# **************************
def pisca_pisca(timer):
    sensor.measure()
#     led.value(not led.value())
    
# **************************
# Criação do timer 0 para o pisca pisca (intervalo de 5 seg)
# **************************
timer0 = Timer(0)
timer0.init(period=5000, mode=Timer.PERIODIC, callback=pisca_pisca)
        
# **************************
# Função manual Relé Kill Switch (V2 no Blynk é alterado na aplicação)
# **************************
def v2_handler(value):
    global modo_manual
    # value é recebido como lista de strings, ex: ['1'] ou ['0']
    estado = int(value[0])

    modo_manual = True  # Sempre que mexer no botão, muda para modo manual
    relay.value(estado)
    print(f"Controle manual: relé = {estado}")
    
#blynk.on("V2", v2_handler)

# **************************
# Função que activa/desactiva relé com base na leitura da temperatura
# **************************
def rele_auto(temp):
    if not modo_manual:  # só atua no modo automático
        if temp > 26.0:
            relay.value(1)
        else:
            relay.value(0)
        
# **************************
# Função que envia o output para os 3 dispositivos (IoT - Blynk; REPL)
# **************************
def output_dispositivos(temp, hum):
    blynk.virtual_write(0, float(temp))             # escreve no pin virtual V0 do blynk (temperatura do ar)
    blynk.virtual_write(1, float(hum))				# escreve no pin virtual V1 do blynk (humidade do ar)
    blynk.virtual_write(2, relay.value())				# escreve no pin virtual V2 do blynk (estado do rele (FAN)
    print(f"T={temp}°C  H={hum}%  Relé={relay.value()}")
    
#     print('Temperatura do ar: ', round(temp,1))             # output para REPL (DEBUG)
#     print('Humidade do ar: ', round(hum,1))                # output para REPL (DEBUG)
    print('--------------------')                             # output para REPL (DEBUG)
    

# *********** Bloco MAIN *********** #

global blynk
conn()     # tenta ligar à rede WiFi
sleep_ms(2000)        # espera de segurança pela rede WiFi
blynk = Blynk(BLYNK_AUTH_TOKEN)


while True:
    blynk.run()                                 # coloca o objecto blynk à espera de dados
    blynk.on("V2", v2_handler)

    try: 
        # sensor.measure() 			# Usar sem Timer
        temp = sensor.temperature()
        hum = sensor.humidity()
        rele_auto(temp)								# chama função rele
        output_dispositivos(temp, hum)             	# chama função de output
    except OSError as e:
        print("Falha na leitura do sensor.")
    
    sleep_ms(5000)		# DHT sensor lento, 5 segundos entre leituras

#interface.active(False)
