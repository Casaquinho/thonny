"""
Autores: 
    Marcelo Henrique Morello Manzo - 23340
    Vitor Henrique Girio Paes - 23340
"""

import network
import time
import ubinascii
import machine
from umqttsimple import MQTTClient

trigger_pin = 5  
echo_pin = 18   
led_verde = machine.Pin(2, machine.Pin.OUT)
led_amarelo = machine.Pin(4, machine.Pin.OUT)
led_vermelho = machine.Pin(16, machine.Pin.OUT)

rede = network.WLAN(network.STA_IF)
rede.active(True)
rede.connect('Lab', '123456789')  
while not rede.isconnected():
    print('.', end="")
    time.sleep(1)
print("Conectado:", rede.ifconfig())

mqtt_server = b'4166df98726c4a0cb6bcbd279ddc281a.s1.eu.hivemq.cloud'
port = 8883
user = b'cotuca'
pwd = b'cotuca'
client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = b'tf_dist'
topic_sub = b'trab_final'
def distanciaHCSR04():
    trigger = machine.Pin(trigger_pin, machine.Pin.OUT)
    echo = machine.Pin(echo_pin, machine.Pin.IN)
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    duration = machine.time_pulse_us(echo, 1)
    distance = duration * 0.034 / 2 
    return distance


def callback(topic, msg):
    try:
        data = eval(msg.decode('utf-8'))  
        ra = data.get('ra')
        led = data.get('led')   
        if ra in ["23326", "23340"]:  
            print(f"Comando recebido: Ligar LED {led}")
            if led == 1:
                led_verde.on()
                led_amarelo.off()
                led_vermelho.off()
            elif led == 2:
                led_verde.off()
                led_amarelo.on()
                led_vermelho.off()
            elif led == 3:
                led_verde.off()
                led_amarelo.off()
                led_vermelho.on()
        else:
            print("RA inválido.")
    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")
try:
    client = MQTTClient(
        client_id,
        mqtt_server,
        port=port,
        user=user,
        password=pwd,
        ssl=True,
        ssl_params={'server_hostname': mqtt_server}
    )
    client.set_callback(callback)
    client.connect()
    print('Conectado ao broker MQTT...')
except OSError as e:
    print(e)
    time.sleep(5)
    machine.reset()

client.subscribe(topic_sub)


while True:
    distancia = distanciaHCSR04()
    msg = f'{{"ra": "23326", "ra2": "23340", "dist": {distancia:.2f}}}'
    client.publish(topic_pub, msg)
    print(f"\nPublicado: {msg}")
    client.check_msg()
    time.sleep(2)
