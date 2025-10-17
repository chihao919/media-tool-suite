# 快速開始 - 螢幕錄製功能

## 5 分鐘快速設定指南

### 步驟 1: 安裝 ffmpeg（1 分鐘）

在終端機執行：
```bash
brew install ffmpeg
```

等待安裝完成後，驗證安裝：
```bash
ffmpeg -version
```

### 步驟 2: 安裝 BlackHole（2 分鐘）

**為什麼需要 BlackHole？**
- macOS 預設無法直接錄製系統音源
- BlackHole 是一個虛擬音訊裝置，讓你可以錄到電腦正在播放的聲音
- **不是麥克風**，是系統內部音訊

**安裝步驟：**
1. 前往 https://github.com/ExistentialAudio/BlackHole
2. 點擊「Releases」
3. 下載 **BlackHole 2ch.pkg**
4. 執行安裝檔

### 步驟 3: 設定音訊路由（2 分鐘）

**建立 Multi-Output Device：**

1. 開啟「**應用程式 > 工具程式 > Audio MIDI Setup**」（音訊 MIDI 設定）

2. 點擊左下角的 **+** 按鈕

3. 選擇「**Create Multi-Output Device**」（建立多輸出裝置）

4. 在右側面板勾選：
   - ✅ **Built-in Output**（讓你聽到聲音）
   - ✅ **BlackHole 2ch**（讓應用程式錄到聲音）

5. 開啟「**系統偏好設定 > 聲音 > 輸出**」

6. 選擇「**Multi-Output Device**」

**完成！** 現在你可以：
- 🎧 從喇叭/耳機聽到聲音（Built-in Output）
- 🎙️ 應用程式可以錄製系統音源（BlackHole）

### 步驟 4: 開始使用（1 分鐘）

1. 執行應用程式：
   ```bash
   python3 main.py
   ```

2. 點擊「**🎥 Screen Record**」分頁

3. 點擊「**Refresh Devices**」按鈕

4. 選擇裝置：
   - **Video Source**: `1: Capture screen 1`（你的螢幕）
   - **Audio Source**: `BlackHole 2ch`（系統音源）

5. 調整設定（可選）：
   - **Framerate**: `30`（標準）或 `60`（高流暢度）
   - **Quality**: `medium`（推薦）或 `high`

6. 點擊「**🔴 Start Recording**」

7. 開始錄製！計時器會顯示錄製時間

8. 完成後點擊「**⏹ Stop Recording**」

9. 檔案會儲存到桌面，名稱類似：
   ```
   screen_recording_20251017_001230.mp4
   ```

## 常見問題快速解答

### Q: 為什麼我錄不到聲音？

**檢查清單：**
- ✅ 已安裝 BlackHole？
- ✅ 已建立 Multi-Output Device？
- ✅ 系統音訊輸出選擇了 Multi-Output Device？
- ✅ 應用程式中選擇了 BlackHole 2ch？
- ✅ 系統音量不是靜音？

### Q: 錄製時我聽不到聲音？

**解決方法：**
- 確認 Multi-Output Device 中**同時勾選**了：
  - Built-in Output（讓你聽到）
  - BlackHole 2ch（讓應用程式錄到）

### Q: 如何只錄螢幕不錄聲音？

**方法 1：** 在開始錄製前，將系統音量設為靜音

**方法 2：** 在應用程式中選擇不同的 Audio Source（例如選擇一個不會有聲音的裝置）

### Q: 可以錄製特定視窗嗎？

目前版本錄製整個螢幕。如果只想錄特定視窗：
1. 先全螢幕錄製
2. 錄完後使用轉檔功能裁切

### Q: 檔案太大怎麼辦？

**減少檔案大小的方法：**
1. 降低 Quality：`high` → `medium` → `low`
2. 降低 Framerate：`60` → `30` → `24`
3. 錄完後使用轉檔功能壓縮

**參考檔案大小（每分鐘）：**
- Ultra 60fps: ~50-80 MB/分鐘
- High 30fps: ~20-30 MB/分鐘
- Medium 30fps: ~10-15 MB/分鐘（推薦）
- Low 24fps: ~5-8 MB/分鐘

## 測試你的設定

**簡單測試：**
1. 在 YouTube 或其他網站播放音樂
2. 開始螢幕錄製
3. 錄製 10 秒
4. 停止錄製
5. 開啟桌面上的影片檔
6. 確認：
   - ✅ 看得到畫面
   - ✅ 聽得到聲音
   - ✅ 滑鼠游標有顯示

**如果成功** → 恭喜！你可以開始使用了 🎉

**如果失敗** → 參考完整指南：`docs/SCREEN_RECORDING_GUIDE.md`

## 進階技巧

### 錄製第二螢幕

如果你有多個螢幕：
1. 點擊「Refresh Devices」
2. 會看到：
   - `1: Capture screen 1`（主螢幕）
   - `2: Capture screen 2`（第二螢幕）
3. 選擇你想錄製的螢幕

### 同時錄製麥克風和系統音源

這個功能目前不支援，但可以：
1. 先用這個 app 錄製螢幕+系統音源
2. 另外用其他軟體錄製麥克風
3. 事後用影片編輯軟體合併

### 定時錄製

目前沒有內建定時功能，但可以：
1. 設定鬧鐘提醒自己停止錄製
2. 或使用 macOS 的腳本功能自動化

## 需要協助？

- 📖 完整指南：`docs/SCREEN_RECORDING_GUIDE.md`
- 🐛 回報問題：GitHub Issues
- 💡 功能建議：歡迎提交 PR

---

**享受你的螢幕錄製體驗！** 🎥✨
