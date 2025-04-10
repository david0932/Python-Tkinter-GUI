import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json
import random
from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv()

class ElectricityMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("環境與電力監測系統")
        
        # 從環境變數載入MQTT設置
        self.power_broker = os.getenv('POWER_BROKER')
        self.env_broker = os.getenv('ENV_BROKER')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        self.topics = {
            os.getenv('POWER_TOPIC'): "電力數據",
            os.getenv('ENV1_TOPIC'): "環境數據1",
            os.getenv('ENV2_TOPIC'): "環境數據2",
            os.getenv('LIGHT_STATUS_TOPIC'): "燈控狀態"
        }
        self.client_id_power = f'python-mqtt-power-{random.randint(0, 1000)}'
        self.client_id_env = f'python-mqtt-env-{random.randint(0, 1000)}'
        self.client_id_env2 = f'python-mqtt-env2-{random.randint(0, 1000)}'
        self.client_id_light = f'python-mqtt-light-{random.randint(0, 1000)}'
        
        # 初始化連接狀態
        self.connection_states = {
            'power': False,
            'env1': False,
            'env2': False,
            'light': False
        }
        
        # 創建GUI元素
        self.create_widgets()
        
        # 初始化燈控狀態
        self.light_states = {'D0': False, 'D1': False, 'D2': False}
        
        # 設置MQTT客戶端
        self.setup_mqtt()

    def setup_mqtt(self):
        # 設置電力數據的MQTT客戶端
        self.power_client = mqtt.Client(client_id=self.client_id_power)
        self.power_client.on_connect = self.on_power_connect
        self.power_client.on_message = self.on_message
        
        # 設置環境數據的MQTT客戶端
        self.env_client = mqtt.Client(client_id=self.client_id_env)
        self.env_client.on_connect = self.on_env_connect
        self.env_client.on_message = self.on_message
        
        # 設置第二個環境數據的MQTT客戶端
        self.env_client2 = mqtt.Client(client_id=self.client_id_env2)
        self.env_client2.on_connect = self.on_env2_connect
        self.env_client2.on_message = self.on_message
        
        # 設置燈控的MQTT客戶端
        self.light_client = mqtt.Client(client_id=self.client_id_light)
        self.light_client.on_connect = self.on_light_connect
        self.light_client.on_message = self.on_message
        try:
            # 連接電力數據broker
            self.power_client.connect(self.power_broker, self.port, 60)
            self.power_client.loop_start()
            
            # 連接環境數據broker
            self.env_client.connect(self.env_broker, self.port, 60)
            self.env_client.loop_start()
            
            # 連接第二個環境數據broker
            self.env_client2.connect(self.env_broker, self.port, 60)
            self.env_client2.loop_start()
            
            # 連接燈控broker
            self.light_client.connect(self.env_broker, self.port, 60)
            self.light_client.loop_start()
        except Exception as e:
            print(f"MQTT連接錯誤: {e}")

    def on_power_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("已連接到電力數據MQTT服務器")
            client.subscribe(os.getenv('POWER_TOPIC'))
            print("已訂閱主題: powermeter/elec110")
            self.connection_states['power'] = True
            self.power_status.configure(text="已連接", style='Connected.TLabel')
        else:
            self.connection_states['power'] = False
            self.power_status.configure(text="未連接", style='Disconnected.TLabel')

    def on_env_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("已連接到環境數據MQTT服務器")
            client.subscribe(os.getenv('ENV1_TOPIC'))
            print("已訂閱主題: modbus/devices/RS-GZCO2WS-N01-2/32")
            self.connection_states['env1'] = True
            self.env1_status.configure(text="已連接", style='Connected.TLabel')
        else:
            self.connection_states['env1'] = False
            self.env1_status.configure(text="未連接", style='Disconnected.TLabel')

    def on_env2_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("已連接到第二個環境數據MQTT服務器")
            client.subscribe(os.getenv('ENV2_TOPIC'))
            print("已訂閱主題: modbus/devices/RS-WS-N01/31")
            self.connection_states['env2'] = True
            self.env2_status.configure(text="已連接", style='Connected.TLabel')
        else:
            self.connection_states['env2'] = False
            self.env2_status.configure(text="未連接", style='Disconnected.TLabel')
        
    def on_light_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("已連接到燈控MQTT服務器")
            client.subscribe(os.getenv('LIGHT_STATUS_TOPIC'))
            print("已訂閱主題: modbus/devices/LC-103H/1")
            self.connection_states['light'] = True
            self.light_status.configure(text="已連接", style='Connected.TLabel')
        else:
            self.connection_states['light'] = False
            self.light_status.configure(text="未連接", style='Disconnected.TLabel')

    def control_light(self, light_id, state):
        command = "ON" if state else "OFF"
        payload = {
            "port": 1,
            "device_id": 1,
            "name": f"D{light_id}-{command}"
        }
        self.light_client.publish(os.getenv('LIGHT_CONTROL_TOPIC'), json.dumps(payload))

    def create_widgets(self):
        # 設置標籤樣式
        self.style = ttk.Style()
        self.style.configure('Connected.TLabel', foreground='green')
        self.style.configure('Disconnected.TLabel', foreground='red')
        
        # 電力數據框架
        power_frame = ttk.LabelFrame(self.root, text="即時電力數據", padding="10")
        power_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # 添加連接狀態標籤
        self.power_status = ttk.Label(power_frame, text="未連接", style='Disconnected.TLabel')
        self.power_status.grid(row=0, column=2, padx=5, pady=5)

        # 環境數據框架1
        env_frame1 = ttk.LabelFrame(self.root, text="環境數據1 (RS-GZCO2WS-N01-2)", padding="10")
        env_frame1.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        # 添加連接狀態標籤
        self.env1_status = ttk.Label(env_frame1, text="未連接", style='Disconnected.TLabel')
        self.env1_status.grid(row=0, column=2, padx=5, pady=5)

        # 環境數據框架2
        env_frame2 = ttk.LabelFrame(self.root, text="環境數據2 (RS-WS-N01)", padding="10")
        env_frame2.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        # 添加連接狀態標籤
        self.env2_status = ttk.Label(env_frame2, text="未連接", style='Disconnected.TLabel')
        self.env2_status.grid(row=0, column=2, padx=5, pady=5)
        
        # 燈控框架
        light_frame = ttk.LabelFrame(self.root, text="燈控狀態", padding="10")
        light_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        # 添加連接狀態標籤
        self.light_status = ttk.Label(light_frame, text="未連接", style='Disconnected.TLabel')
        #self.light_status.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self.light_status.grid(row=0, column=6, padx=5, pady=5)

        # 創建標籤和數值顯示
        self.values = {}
        
        # 設置按鈕樣式
        self.style = ttk.Style()
        self.style.configure('Green.TButton', background='green')
        self.style.configure('Red.TButton', background='red')
        
        # 燈控按鈕
        self.light_buttons = {}
        for i in range(3):
            light_label = ttk.Label(light_frame, text=f"燈 {i}")
            light_label.grid(row=0, column=i*2, padx=5, pady=5)
            
            button = ttk.Button(light_frame, text="開啟", style='Red.TButton',
                               command=lambda x=i: self.control_light(x, not self.light_states[f'D{x}']))
            button.grid(row=0, column=i*2+1, padx=5, pady=5)
            
            self.light_buttons[f'D{i}'] = button
        
        # 電力參數
        power_parameters = {
            'v': '電壓 (V)',
            'i': '電流 (A)',
            'active_power': '有功功率 (W)',
            'freq': '頻率 (Hz)',
            'pf': '功率因數'
        }

        # 環境參數
        env_parameters = {
            'Temperature': '溫度 (°C)',
            'Humidity': '濕度 (%)',
            'CO2': 'CO2 (ppm)',
            'Light': '光照 (lux)'
        }

        # 添加電力參數
        for i, (key, label) in enumerate(power_parameters.items()):
            ttk.Label(power_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.values[f'power_{key}'] = ttk.Label(power_frame, text="--")
            self.values[f'power_{key}'].grid(row=i, column=1, padx=5, pady=5, sticky="e")

        # 添加環境參數1
        for i, (key, label) in enumerate(env_parameters.items()):
            ttk.Label(env_frame1, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.values[f'env1_{key}'] = ttk.Label(env_frame1, text="--")
            self.values[f'env1_{key}'].grid(row=i, column=1, padx=5, pady=5, sticky="e")

        # 添加環境參數2（只顯示溫度和濕度）
        env2_parameters = {
            'Temperature': '溫度 (°C)',
            'Humidity': '濕度 (%)'
        }
        for i, (key, label) in enumerate(env2_parameters.items()):
            ttk.Label(env_frame2, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.values[f'env2_{key}'] = ttk.Label(env_frame2, text="--")
            self.values[f'env2_{key}'].grid(row=i, column=1, padx=5, pady=5, sticky="e")

    def on_connect(self, client, userdata, flags, rc):
        print("已連接到MQTT服務器")
        for topic in self.topics:
            client.subscribe(topic)
            print(f"已訂閱主題: {topic}")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode('utf-8', 'ignore'))
            topic = msg.topic
            
            # 根據主題更新相應的GUI顯示
            if topic == "powermeter/elec110":
                for key in data:
                    value_key = f'power_{key}'
                    if value_key in self.values:
                        value = round(float(data[key]), 2) if isinstance(data[key], (int, float)) else data[key]
                        self.values[value_key].config(text=str(value))
            elif topic == "modbus/devices/RS-GZCO2WS-N01-2/32":
                for key in data:
                    value_key = f'env1_{key}'
                    if value_key in self.values:
                        value = round(float(data[key]), 2) if isinstance(data[key], (int, float)) else data[key]
                        self.values[value_key].config(text=str(value))
            elif topic == "modbus/devices/RS-WS-N01/31":
                for key in data:
                    value_key = f'env2_{key}'
                    if value_key in self.values:
                        value = round(float(data[key]), 2) if isinstance(data[key], (int, float)) else data[key]
                        self.values[value_key].config(text=str(value))
            elif topic == "modbus/devices/LC-103H/1":
                for key, value in data.items():
                    if key in self.light_buttons:
                        self.light_states[key] = bool(value)
                        button_text = "關閉" if self.light_states[key] else "開啟"
                        button_style = 'Green.TButton' if self.light_states[key] else 'Red.TButton'
                        self.light_buttons[key].configure(text=button_text, style=button_style)
        except Exception as e:
            print(f"數據處理錯誤: {e}")

def main():
    root = tk.Tk()
    app = ElectricityMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()