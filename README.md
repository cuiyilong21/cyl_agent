# 🌤️ cyl_agent - 上海天气查询应用

AI 助手创建的 Python GUI 天气应用，支持查询上海15天天气预报。

## ✨ 功能特点

- 🌡️ **实时天气** - 显示当前温度、天气状况
- 📅 **15天预报** - 查看未来15天的天气预报
- 🎨 **精美UI** - 使用 tkinter 构建的现代化界面
- 💧 **详细信息** - 湿度、风速、能见度、降水概率
- 🆓 **免费API** - 使用 Open-Meteo，无需 API Key

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python shanghai_weather.py
```

## 📋 系统要求

- Python 3.6+
- macOS / Windows / Linux

## 🛠️ 技术栈

- **Python 3** - 核心语言
- **tkinter** - GUI 界面
- **Open-Meteo API** - 天气数据 (免费，无需注册)
- **requests** - HTTP 请求

## 📸 界面预览

应用启动后会显示：
- 当前天气卡片（大图标 + 温度 + 详细数据）
- 15天天气预报列表（每天一行，包含图标、温度、降水概率）

## 🔧 自定义

如果你想查询其他城市，可以修改 `WeatherApp` 类中的坐标：

```python
# 修改为你想查询的城市坐标
SHANGHAI_LAT = 31.23   # 纬度
SHANGHAI_LON = 121.47  # 经度
```

## 📄 开源协议

MIT License

---

Created by AI Assistant 🤖
