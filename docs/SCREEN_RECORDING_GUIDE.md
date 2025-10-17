# Screen Recording Guide - 螢幕錄製使用指南

## 功能說明

這個螢幕錄製功能可以讓你同時錄製電腦螢幕畫面和系統音源（不是從麥克風收音，而是直接從電腦音源錄音）。

## 系統需求

### 1. 安裝 ffmpeg

在 macOS 上，使用 Homebrew 安裝 ffmpeg：

```bash
brew install ffmpeg
```

### 2. 安裝 BlackHole（錄製系統音源必需）

要錄製系統音源（而不是麥克風），你需要安裝 **BlackHole** 虛擬音訊裝置：

1. 前往 [BlackHole GitHub](https://github.com/ExistentialAudio/BlackHole)
2. 下載並安裝 BlackHole 2ch 或 16ch
3. 安裝後需要進行音訊設定

### 3. 設定系統音訊

安裝 BlackHole 後，需要設定音訊路由：

#### 方法 1: 使用 Audio MIDI Setup（音訊 MIDI 設定）

1. 開啟 **應用程式 > 工具程式 > Audio MIDI Setup**
2. 點擊左下角的 **+** 按鈕
3. 選擇 **Create Multi-Output Device**（建立多輸出裝置）
4. 勾選：
   - **Built-in Output**（內建輸出 - 讓你聽到聲音）
   - **BlackHole 2ch**（錄製用）
5. 在 **System Preferences > Sound > Output**（系統偏好設定 > 聲音 > 輸出）
6. 選擇剛建立的 **Multi-Output Device**

#### 方法 2: 使用 Soundflower 或 Loopback

可以考慮使用其他音訊路由軟體，如：
- [Loopback](https://rogueamoeba.com/loopback/)（付費但更簡單）
- Soundflower（免費但已停止維護）

## 使用方式

### 1. 開啟應用程式

啟動 **檔案豪幫手** 應用程式，點擊 **🎥 Screen Record** 分頁。

### 2. 設定錄製參數

#### Framerate（影格率）
- **24 fps**: 電影風格，檔案較小
- **30 fps**: 標準錄製（推薦）
- **60 fps**: 高流暢度，適合遊戲或快速動作

#### Quality（品質）
- **low**: 低品質，檔案最小
- **medium**: 中等品質（推薦）
- **high**: 高品質
- **ultra**: 超高品質，檔案最大

### 3. 選擇裝置

#### Video Source（影像來源）
點擊 **Refresh Devices** 按鈕，會列出所有可用的影像裝置：
- **Capture screen 1**: 主螢幕
- **Capture screen 2**: 第二螢幕（如果有）
- **FaceTime HD Camera**: 內建攝影機

選擇你想錄製的螢幕。

#### Audio Source（音源來源）
選擇音訊輸入裝置：
- 如果已設定 **Multi-Output Device + BlackHole**，選擇 **BlackHole 2ch**
- 如果要錄製麥克風，選擇 **Built-in Microphone**

### 4. 開始錄製

1. 點擊 **🔴 Start Recording** 按鈕
2. macOS 會要求螢幕錄製權限（第一次使用時）
   - 前往 **System Preferences > Security & Privacy > Privacy > Screen Recording**
   - 勾選你的應用程式
3. 錄製狀態會顯示為 **🔴 Recording...**
4. 計時器會顯示錄製時間

### 5. 停止錄製

1. 點擊 **⏹ Stop Recording** 按鈕
2. 錄製會儲存到桌面
3. 檔案名稱格式：`screen_recording_YYYYMMDD_HHMMSS.mp4`

## 輸出格式

- **影片格式**: MP4
- **影片編碼**: H.264 (libx264)
- **音訊編碼**: AAC
- **音訊位元率**: 192 kbps
- **音訊取樣率**: 48000 Hz

## 常見問題

### Q: 沒有聲音？

A: 確認以下事項：
1. 已安裝 BlackHole
2. 已建立並選擇 Multi-Output Device
3. 在應用程式中選擇正確的音訊裝置（BlackHole 2ch）
4. 確認系統音量不是靜音

### Q: 錄製時聽不到聲音？

A: 如果只選擇 BlackHole 作為輸出，你不會聽到聲音。必須建立 **Multi-Output Device** 並同時勾選：
- Built-in Output（讓你聽到）
- BlackHole（讓應用程式錄到）

### Q: 找不到 ffmpeg？

A: 安裝 ffmpeg：
```bash
brew install ffmpeg
```

### Q: 權限被拒絕？

A: 前往：
**System Preferences > Security & Privacy > Privacy**

並確認已授權：
- **Screen Recording**（螢幕錄製）
- **Microphone**（如果要錄麥克風）

### Q: 錄製的影片很大？

A: 調整以下設定來減少檔案大小：
- 降低 Framerate（例如從 60 改為 30）
- 降低 Quality（例如從 high 改為 medium）
- 如果只需要螢幕特定區域，可以之後用轉檔功能裁切

## 技術細節

### 使用的技術
- **ffmpeg** 搭配 **avfoundation** 輸入格式
- 使用 Python `subprocess` 模組執行 ffmpeg
- Builder Pattern 設計模式

### 程式碼架構
- `src/screen_recorder.py`: 錄製核心邏輯
- `src/media_converter.py`: UI 介面
- `tests/test_screen_recorder.py`: 單元測試

### ffmpeg 指令範例

實際執行的 ffmpeg 指令類似：

```bash
ffmpeg -f avfoundation \
  -framerate 30 \
  -capture_cursor 1 \
  -i "1:0" \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -c:a aac \
  -b:a 192k \
  -ar 48000 \
  -y output.mp4
```

其中：
- `-i "1:0"`: 裝置 1（螢幕）和裝置 0（音訊）
- `-capture_cursor 1`: 錄製滑鼠游標
- `-crf 23`: 品質設定（值越小品質越高，18-28 是常用範圍）
- `-preset medium`: 編碼速度預設

## 進階使用

### 自訂輸出路徑

目前預設儲存到桌面，如果需要自訂路徑，可以修改程式碼：

```python
# 在 start_recording() 中
output_path = filedialog.asksaveasfilename(
    defaultextension=".mp4",
    filetypes=[("MP4 Video", "*.mp4")]
)
```

### 錄製特定區域

可以加入 `-s` 參數指定解析度：

```bash
-s 1920x1080
```

### 同時錄製螢幕和攝影機

建立兩個輸入源並使用 filter_complex 合併。

## 參考資源

- [ffmpeg avfoundation documentation](https://ffmpeg.org/ffmpeg-devices.html#avfoundation)
- [BlackHole GitHub](https://github.com/ExistentialAudio/BlackHole)
- [macOS Screen Recording Guide](https://support.apple.com/guide/mac-help/take-a-screenshot-or-screen-recording-mh26782/mac)

---

如有問題或建議，請聯繫開發團隊。
