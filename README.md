# 環境與電力監測系統

這是一個基於Python Tkinter和MQTT協議開發的環境與電力監測系統，提供即時電力數據監測、環境參數監測以及燈控功能。

## 功能特點

### 1. 電力監測
- 即時監測電壓 (V)
- 即時監測電流 (A)
- 即時監測有功功率 (W)
- 即時監測頻率 (Hz)
- 即時監測功率因數

### 2. 環境監測
#### 環境感測器1 (RS-GZCO2WS-N01-2)
- 溫度監測 (°C)
- 濕度監測 (%)
- CO2濃度監測 (ppm)
- 光照強度監測 (lux)

#### 環境感測器2 (RS-WS-N01)
- 溫度監測 (°C)
- 濕度監測 (%)

### 3. 燈控功能
- 支援3組獨立燈具控制
- 即時顯示燈具開關狀態
- 可透過GUI介面進行開關操作

## 系統需求
- Python >= 3.12
- paho-mqtt
- tkinter (Python標準庫)

## 安裝說明

1. 安裝相依套件：
```bash
pip install paho-mqtt
```

2. 執行程式：
```bash
python dashboard.py
```

## MQTT配置說明

為了保護系統安全，MQTT連接資訊需要通過環境變數配置。請在專案根目錄建立 `.env` 檔案，並設置以下環境變數：

```ini
# MQTT Broker設定
MQTT_BROKER_POWER=<電力數據broker位址>
MQTT_BROKER_ENV=<環境數據broker位址>
MQTT_PORT=1883

# MQTT主題設定
MQTT_TOPIC_POWER=<電力數據主題>
MQTT_TOPIC_ENV1=<環境數據1主題>
MQTT_TOPIC_ENV2=<環境數據2主題>
MQTT_TOPIC_LIGHT=<燈控狀態主題>
MQTT_TOPIC_CONTROL=<燈控命令主題>
```

請向系統管理員獲取正確的配置值。

## 資料格式

### 電力數據格式
```json
{
    "v": "電壓值",
    "i": "電流值",
    "active_power": "有功功率值",
    "freq": "頻率值",
    "pf": "功率因數值"
}
```

### 環境數據格式
```json
{
    "Temperature": "溫度值",
    "Humidity": "濕度值",
    "CO2": "CO2濃度值",
    "Light": "光照強度值"
}
```

### 燈控命令格式
```json
{
    "port": 1,
    "device_id": 1,
    "name": "Dx-ON/OFF"  # x為燈具編號(0-2)，ON/OFF為控制命令
}
```

## 使用者介面
- 主視窗分為四個區域：電力數據、環境數據1、環境數據2和燈控
- 每個區域都有連接狀態指示燈
- 所有數據即時更新
- 燈控按鈕可直接控制對應的燈具

## 錯誤處理
- MQTT連接失敗時會顯示錯誤訊息
- 連接狀態即時更新
- 數據解析錯誤時會記錄到控制台

<img src="https://github.com/david0932/electricity-dashboard/blob/master/image/screenshot.png" alt="Screenshot" width="400" />