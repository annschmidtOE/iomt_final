import paho.mqtt.client as mqtt

pille1 = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Forbundet til broker!")
        client.subscribe("pilledata")
    else:
        print(f"Forbindelsesfejl med kode {rc}")

def on_message(client, userdata, msg):
    global pille1
    pille1 = msg.payload.decode()
    print(f"Besked modtaget: {pille1}")


    send_to_vm(pille1)

def send_to_vm(data):
    try:
        
        publish_client = mqtt.Client()
        vm_broker_ip = "172.201.226.158"
        publish_client.connect(vm_broker_ip, 1883, 60)
        

        publish_client.publish("pilledata", data)
        print(f"Pilledata sendt til VM: {data}")
        
        publish_client.disconnect()
    except Exception as e:
        print(f"Fejl ved sending til VM: {e}")

broker_ip = "localhost"
client = mqtt.Client()
client.enable_logger()

client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Forbinder til MQTT broker på {broker_ip}...")
    client.connect(broker_ip, 1883, 60)
    client.loop_forever()
except Exception as e:
    print(f"Der opstod en fejl: {e}")
