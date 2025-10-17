# 重開機後的設定步驟

## ✅ 重開機後請按照以下步驟操作：

### 步驟 1: 驗證 BlackHole 安裝

開啟終端機，執行：
```bash
cd ~/Downloads/splitvideo
system_profiler SPAudioDataType | grep -i blackhole
```

如果看到 `BlackHole 2ch:` 就表示安裝成功！

### 步驟 2: 設定 Multi-Output Device

1. 開啟「**應用程式 > 工具程式 > Audio MIDI Setup**」
   - 或按 `⌘ + Space` 輸入 "Audio MIDI"

2. 點擊左下角的 **+** 按鈕

3. 選擇「**Create Multi-Output Device**」

4. 在右側勾選：
   - ✅ **Built-in Output** (讓你聽到聲音)
   - ✅ **BlackHole 2ch** (讓應用程式錄到聲音)

   **兩個都要勾選！**

5. (可選) 重新命名為 "Recording + Playback"

### 步驟 3: 設定系統音訊輸出

1. 開啟「**系統偏好設定 > 聲音 > 輸出**」

2. 選擇「**Multi-Output Device**」

3. 測試：播放 YouTube 音樂，確認能聽到聲音

### 步驟 4: 啟動應用程式並測試

1. 在終端機執行：
```bash
cd ~/Downloads/splitvideo
python3 main.py
```

2. 點擊「**🎥 Screen Record**」分頁

3. 點擊「**Refresh Devices**」按鈕

4. 設定裝置：
   - **Video Source**: 選擇 `3: Capture screen 0`
   - **Audio Source**: 選擇 `BlackHole 2ch` ← 這就是系統音源！

5. 點擊「**🔴 Start Recording**」

6. 播放 YouTube 音樂測試

7. 錄製 10 秒後，點擊「**⏹ Stop Recording**」

8. 檢查桌面上的影片檔案，應該有畫面和系統音源！

### 🎉 完成！

你現在可以錄製：
- ✅ 螢幕畫面
- ✅ 系統音源（YouTube、Spotify 等）
- ✅ 滑鼠游標

---

## 📝 如果遇到問題

### Q: 重開機後找不到 BlackHole？

執行以下檢查：
```bash
# 檢查驅動檔案
ls -la /Library/Audio/Plug-Ins/HAL/ | grep BlackHole

# 列出所有音訊裝置
ffmpeg -f avfoundation -list_devices true -i "" 2>&1 | grep -i audio
```

### Q: 聽不到聲音？

確認 Multi-Output Device 中**同時勾選**了：
- Built-in Output (讓你聽到)
- BlackHole 2ch (讓應用程式錄到)

並且系統音訊輸出選擇了 Multi-Output Device。

### Q: 錄不到聲音？

1. 確認應用程式中選擇了 `BlackHole 2ch`
2. 確認系統音訊輸出是 Multi-Output Device
3. 播放音樂確認有聲音

---

## 📖 詳細文件

- `SETUP_SYSTEM_AUDIO.md` - 完整設定指南
- `docs/SCREEN_RECORDING_GUIDE.md` - 螢幕錄製指南
- `docs/QUICK_START_SCREEN_RECORDING.md` - 快速開始

祝錄製順利！🎥✨
