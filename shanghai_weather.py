#!/usr/bin/env python3
"""
上海天气查询应用 - 15天天气预报
使用 Open-Meteo API (免费，无需 API Key)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class WeatherApp:
    """上海天气查询应用"""
    
    # 上海坐标
    SHANGHAI_LAT = 31.23
    SHANGHAI_LON = 121.47
    SHANGHAI_NAME = "上海"
    
    # 天气代码映射
    WEATHER_CODES = {
        0: ("☀️", "晴朗"),
        1: ("🌤️", "大部晴朗"),
        2: ("⛅", "多云"),
        3: ("☁️", "阴天"),
        45: ("🌫️", "雾"),
        48: ("🌫️", "雾凇"),
        51: ("🌧️", "毛毛雨"),
        53: ("🌧️", "中度毛毛雨"),
        55: ("🌧️", "大毛毛雨"),
        61: ("🌦️", "小雨"),
        63: ("🌧️", "中雨"),
        65: ("⛈️", "大雨"),
        71: ("🌨️", "小雪"),
        73: ("🌨️", "中雪"),
        75: ("❄️", "大雪"),
        80: ("🌦️", "阵雨"),
        81: ("🌧️", "强阵雨"),
        82: ("⛈️", "暴雨"),
        95: ("⛈️", "雷雨"),
        96: ("⛈️", "雷雨伴冰雹"),
        99: ("⛈️", "强雷雨伴冰雹"),
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌤️ 上海天气查询 - 15天预报")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f8")
        
        # 数据存储
        self.weather_data: Optional[Dict] = None
        
        self._setup_ui()
        self.fetch_weather()  # 自动获取天气
    
    def _setup_ui(self):
        """设置用户界面"""
        # 标题
        title_frame = tk.Frame(self.root, bg="#1a73e8", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🌤️ 上海天气查询",
            font=("Microsoft YaHei", 24, "bold"),
            fg="white",
            bg="#1a73e8"
        )
        title_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 控制区域
        control_frame = tk.Frame(self.root, bg="#f0f4f8", padx=20, pady=15)
        control_frame.pack(fill=tk.X)
        
        # 刷新按钮
        self.refresh_btn = tk.Button(
            control_frame,
            text="🔄 刷新天气",
            font=("Microsoft YaHei", 12),
            bg="#1a73e8",
            fg="white",
            activebackground="#1557b0",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.fetch_weather
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_label = tk.Label(
            control_frame,
            text="",
            font=("Microsoft YaHei", 10),
            bg="#f0f4f8",
            fg="#666"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # 当前天气卡片
        self.current_frame = tk.Frame(
            self.root,
            bg="white",
            highlightbackground="#ddd",
            highlightthickness=1,
            padx=20,
            pady=20
        )
        self.current_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self._create_current_weather_display()
        
        # 15天预报区域
        forecast_label = tk.Label(
            self.root,
            text="📅 15天天气预报",
            font=("Microsoft YaHei", 16, "bold"),
            bg="#f0f4f8",
            fg="#333"
        )
        forecast_label.pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # 创建Canvas和滚动条
        canvas_frame = tk.Frame(self.root, bg="#f0f4f8")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f4f8")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _create_current_weather_display(self):
        """创建当前天气显示"""
        # 清除旧内容
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        
        # 左侧：大图标和温度
        self.current_icon_label = tk.Label(
            self.current_frame,
            text="🌡️",
            font=("Microsoft YaHei", 72),
            bg="white"
        )
        self.current_icon_label.pack(side=tk.LEFT, padx=20)
        
        # 中间：温度和描述
        info_frame = tk.Frame(self.current_frame, bg="white")
        info_frame.pack(side=tk.LEFT, padx=20)
        
        self.current_temp_label = tk.Label(
            info_frame,
            text="--°C",
            font=("Microsoft YaHei", 48, "bold"),
            bg="white",
            fg="#1a73e8"
        )
        self.current_temp_label.pack(anchor=tk.W)
        
        self.current_desc_label = tk.Label(
            info_frame,
            text="加载中...",
            font=("Microsoft YaHei", 18),
            bg="white",
            fg="#666"
        )
        self.current_desc_label.pack(anchor=tk.W)
        
        # 右侧：详细信息
        detail_frame = tk.Frame(self.current_frame, bg="white")
        detail_frame.pack(side=tk.RIGHT, padx=40)
        
        details = [
            ("💨 风速", "wind_label", "-- km/h"),
            ("💧 湿度", "humidity_label", "--%"),
            ("🧭 风向", "direction_label", "--"),
            ("👁️ 能见度", "visibility_label", "-- km"),
        ]
        
        for icon_text, attr_name, default_text in details:
            row = tk.Frame(detail_frame, bg="white")
            row.pack(anchor=tk.W, pady=5)
            
            tk.Label(
                row,
                text=icon_text,
                font=("Microsoft YaHei", 12),
                bg="white",
                fg="#333",
                width=12,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            label = tk.Label(
                row,
                text=default_text,
                font=("Microsoft YaHei", 12, "bold"),
                bg="white",
                fg="#1a73e8"
            )
            label.pack(side=tk.LEFT)
            setattr(self, attr_name, label)
    
    def _get_weather_info(self, code: int) -> tuple:
        """获取天气代码对应的图标和描述"""
        return self.WEATHER_CODES.get(code, ("❓", "未知"))
    
    def fetch_weather(self):
        """获取天气数据"""
        self.status_label.config(text="⏳ 正在获取天气数据...")
        self.refresh_btn.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # Open-Meteo API - 免费，无需 API Key
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.SHANGHAI_LAT}&"
                f"longitude={self.SHANGHAI_LON}&"
                f"current_weather=true&"
                f"daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max&"
                f"timezone=Asia/Shanghai&"
                f"forecast_days=15"
            )
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            self.weather_data = response.json()
            self._update_display()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.config(text=f"✅ 最后更新: {now}")
            
        except requests.RequestException as e:
            self.status_label.config(text=f"❌ 获取失败: {str(e)}")
            messagebox.showerror("错误", f"获取天气数据失败:\n{str(e)}")
        except Exception as e:
            self.status_label.config(text=f"❌ 错误: {str(e)}")
            messagebox.showerror("错误", f"发生错误:\n{str(e)}")
        finally:
            self.refresh_btn.config(state=tk.NORMAL)
    
    def _update_display(self):
        """更新显示"""
        if not self.weather_data:
            return
        
        # 更新当前天气
        current = self.weather_data.get("current_weather", {})
        weather_code = current.get("weathercode", 0)
        icon, desc = self._get_weather_info(weather_code)
        
        self.current_icon_label.config(text=icon)
        self.current_temp_label.config(text=f"{current.get('temperature', '--')}°C")
        self.current_desc_label.config(text=desc)
        
        self.wind_label.config(text=f"{current.get('windspeed', '--')} km/h")
        self.direction_label.config(text=f"{current.get('winddirection', '--')}°")
        
        # 获取湿度和能见度（需要从另一个端点获取）
        self._fetch_additional_data()
        
        # 更新15天预报
        self._update_forecast()
    
    def _fetch_additional_data(self):
        """获取额外的天气数据（湿度、能见度等）"""
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.SHANGHAI_LAT}&"
                f"longitude={self.SHANGHAI_LON}&"
                f"hourly=relativehumidity_2m,visibility&"
                f"timezone=Asia/Shanghai&"
                f"forecast_days=1"
            )
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            hourly = data.get("hourly", {})
            humidity_list = hourly.get("relativehumidity_2m", [])
            visibility_list = hourly.get("visibility", [])
            
            if humidity_list:
                current_hour = datetime.now().hour
                humidity = humidity_list[min(current_hour, len(humidity_list) - 1)]
                self.humidity_label.config(text=f"{humidity}%")
            
            if visibility_list:
                current_hour = datetime.now().hour
                visibility = visibility_list[min(current_hour, len(visibility_list) - 1)]
                # 能见度单位是米，转换为公里
                visibility_km = visibility / 1000
                self.visibility_label.config(text=f"{visibility_km:.1f} km")
                
        except Exception:
            pass  # 非关键数据，失败不显示错误
    
    def _update_forecast(self):
        """更新15天预报显示"""
        # 清除旧内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        daily = self.weather_data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        weather_codes = daily.get("weathercode", [])
        precip_probs = daily.get("precipitation_probability_max", [])
        
        # 创建预报卡片
        for i, date_str in enumerate(dates):
            if i >= len(max_temps):
                break
            
            # 解析日期
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
            today_str = " (今天)" if i == 0 else ""
            
            # 获取天气信息
            code = weather_codes[i] if i < len(weather_codes) else 0
            icon, desc = self._get_weather_info(code)
            
            max_temp = max_temps[i]
            min_temp = min_temps[i]
            precip = precip_probs[i] if i < len(precip_probs) else 0
            
            # 创建卡片
            card = tk.Frame(
                self.scrollable_frame,
                bg="white",
                highlightbackground="#ddd",
                highlightthickness=1,
                padx=15,
                pady=15
            )
            card.pack(fill=tk.X, pady=5)
            
            # 日期
            date_label = tk.Label(
                card,
                text=f"{date_str} {weekday}{today_str}",
                font=("Microsoft YaHei", 12, "bold"),
                bg="white",
                fg="#333"
            )
            date_label.pack(anchor=tk.W)
            
            # 天气信息行
            info_row = tk.Frame(card, bg="white")
            info_row.pack(fill=tk.X, pady=10)
            
            # 天气图标
            tk.Label(
                info_row,
                text=icon,
                font=("Microsoft YaHei", 36),
                bg="white"
            ).pack(side=tk.LEFT, padx=10)
            
            # 天气描述
            tk.Label(
                info_row,
                text=desc,
                font=("Microsoft YaHei", 14),
                bg="white",
                fg="#666",
                width=10
            ).pack(side=tk.LEFT, padx=10)
            
            # 温度
            temp_frame = tk.Frame(info_row, bg="white")
            temp_frame.pack(side=tk.LEFT, padx=20)
            
            tk.Label(
                temp_frame,
                text=f"{int(max_temp)}°",
                font=("Microsoft YaHei", 20, "bold"),
                bg="white",
                fg="#ff5722"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                temp_frame,
                text=" / ",
                font=("Microsoft YaHei", 16),
                bg="white",
                fg="#999"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                temp_frame,
                text=f"{int(min_temp)}°",
                font=("Microsoft YaHei", 20, "bold"),
                bg="white",
                fg="#2196f3"
            ).pack(side=tk.LEFT)
            
            # 降水概率
            precip_frame = tk.Frame(info_row, bg="white")
            precip_frame.pack(side=tk.RIGHT, padx=20)
            
            precip_color = "#4caf50" if precip < 30 else "#ff9800" if precip < 60 else "#f44336"
            tk.Label(
                precip_frame,
                text=f"💧 {precip}%",
                font=("Microsoft YaHei", 12, "bold"),
                bg="white",
                fg=precip_color
            ).pack()


def main():
    """主函数"""
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
