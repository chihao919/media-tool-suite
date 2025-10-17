# 設定系統音源錄製 - 完整步驟指南

## 目標
讓應用程式能夠錄製**電腦正在播放的聲音**（不是麥克風），例如：
- YouTube 影片的聲音
- Spotify 音樂
- 遊戲音效
- 任何電腦播放的音訊

## 步驟 1: 安裝 BlackHole

### 方法 A: 使用 Homebrew（推薦）

```bash
brew install blackhole-2ch
```

**注意**：安裝完成後需要**重新啟動電腦**才能生效。

### 方法 B: 手動下載安裝

1. 前往 https://github.com/ExistentialAudio/BlackHole/releases
2. 下載 **BlackHole2ch.v0.6.1.pkg**
3. 雙擊安裝
4. 重新啟動電腦

## 步驟 2: 驗證 BlackHole 安裝

重新啟動後，檢查 BlackHole 是否已安裝：

### 方法 1: 使用終端機
```bash
system_profiler SPAudioDataType | grep -i blackhole
```

應該看到類似輸出：
```
BlackHole 2ch:
```

### 方法 2: 使用 Audio MIDI Setup
1. 開啟「**應用程式 > 工具程式 > Audio MIDI Setup**」
2. 在左側裝置列表中應該看到「**BlackHole 2ch**」

## 步驟 3: 建立 Multi-Output Device

**為什麼需要 Multi-Output Device？**
- 如果只選擇 BlackHole 作為輸出，你會聽不到聲音（因為聲音只送到 BlackHole）
- Multi-Output Device 可以**同時**把聲音送到：
  - 你的喇叭/耳機（讓你聽到）
  - BlackHole（讓應用程式錄到）

**設定步驟：**

1. 開啟「**應用程式 > 工具程式 > Audio MIDI Setup**」
   - 快捷鍵：`⌘ + Space` 輸入 "Audio MIDI"

2. 點擊左下角的 **+** 按鈕

3. 選擇「**Create Multi-Output Device**」（建立多輸出裝置）

4. 在右側面板勾選以下裝置：
   - ✅ **Built-in Output**（或你的喇叭/耳機名稱）
   - ✅ **BlackHole 2ch**

   **重要**：兩個都要勾選！

5. （可選）在上方將此裝置重新命名為「**Recording + Playback**」方便識別

6. 關閉 Audio MIDI Setup 視窗

## 步驟 4: 設定系統音訊輸出

1. 開啟「**系統偏好設定 > 聲音**」（或系統設定 > 聲音）
   - macOS Ventura 以上：`⌘ + Space` 輸入 "聲音設定"

2. 點擊「**輸出**」分頁

3. 選擇「**Multi-Output Device**」（或你命名的「Recording + Playback」）

4. 測試：播放音樂，確認你能聽到聲音

## 步驟 5: 在應用程式中設定

1. 開啟「檔案豪幫手」應用程式：
   ```bash
   python3 main.py
   ```

2. 點擊「**🎥 Screen Record**」分頁

3. 點擊「**Refresh Devices**」按鈕

4. 在「**Audio Source**」下拉選單中選擇：
   - **BlackHole 2ch** ← 選這個！

5. 在「**Video Source**」中選擇你的螢幕

6. 點擊「**🔴 Start Recording**」開始錄製

## 步驟 6: 測試錄製

**簡單測試：**

1. 在 YouTube 或 Spotify 播放音樂
2. 開始螢幕錄製（按照步驟 5）
3. 錄製 10 秒
4. 停止錄製
5. 開啟桌面上的 MP4 檔案
6. 確認：
   - ✅ 看得到畫面
   - ✅ 聽得到音樂（系統音源，不是麥克風）

## 常見問題排解

### Q1: 聽不到聲音？

**檢查清單：**
1. Multi-Output Device 中是否同時勾選了：
   - Built-in Output（或你的喇叭）
   - BlackHole 2ch
2. 系統音訊輸出是否選擇了 Multi-Output Device
3. 音量是否靜音

**解決方法：**
```bash
# 在終端機查看當前音訊裝置
system_profiler SPAudioDataType
```

### Q2: 錄不到聲音？

**檢查清單：**
1. 是否已重新啟動電腦（安裝 BlackHole 後）
2. 應用程式中是否選擇了 BlackHole 2ch
3. 是否有播放音訊（YouTube、Spotify 等）
4. 系統音訊輸出是否選擇了 Multi-Output Device

**測試 BlackHole：**
```bash
# 查看可用的音訊裝置
ffmpeg -f avfoundation -list_devices true -i ""
```

應該看到類似輸出：
```
[AVFoundation audio devices:
[0] BlackHole 2ch
[1] MacBook Pro Microphone
...
```

### Q3: 安裝 BlackHole 後無法開機？

這種情況極少發生，但如果遇到：

1. 開機時按住 `⌘ + R` 進入 Recovery Mode
2. 開啟終端機
3. 移除 BlackHole：
   ```bash
   rm -rf /Library/Audio/Plug-Ins/HAL/BlackHole2ch.driver
   ```
4. 重新啟動

### Q4: 想恢復原本的音訊設定？

**方法 1：** 在系統偏好設定 > 聲音 > 輸出，選擇「**Built-in Output**」

**方法 2：** 解除安裝 BlackHole：
```bash
brew uninstall blackhole-2ch
```

或手動刪除：
```bash
sudo rm -rf /Library/Audio/Plug-Ins/HAL/BlackHole2ch.driver
```

## 進階設定

### 調整 Multi-Output Device 音量

在 Audio MIDI Setup 中：
1. 選擇 Multi-Output Device
2. 在右側可以調整每個裝置的音量
3. 建議兩個都設為相同音量

### 建立 Aggregate Device（聚合裝置）

如果你想同時錄製系統音源和麥克風：

1. 在 Audio MIDI Setup 中點擊 **+**
2. 選擇「**Create Aggregate Device**」
3. 勾選：
   - BlackHole 2ch
   - Built-in Microphone
4. 在應用程式中選擇這個 Aggregate Device

## 快速參考圖解

```
[你播放音樂]
    ↓
[系統音訊輸出: Multi-Output Device]
    ├─→ [Built-in Output] → 🔊 你聽到聲音
    └─→ [BlackHole 2ch]  → 🎥 應用程式錄到聲音
```

## 檢查清單

在開始錄製前，確認以下項目：

- [ ] BlackHole 已安裝並重新啟動電腦
- [ ] 建立了 Multi-Output Device
- [ ] Multi-Output Device 中勾選了 Built-in Output 和 BlackHole
- [ ] 系統音訊輸出選擇了 Multi-Output Device
- [ ] 應用程式中選擇了 BlackHole 2ch 作為 Audio Source
- [ ] 測試播放音樂，確認能聽到聲音
- [ ] 測試錄製 10 秒，確認影片有聲音

## 需要協助？

如果按照上述步驟仍無法正常運作：

1. 查看完整指南：`docs/SCREEN_RECORDING_GUIDE.md`
2. 查看快速指南：`docs/QUICK_START_SCREEN_RECORDING.md`
3. 回報問題：GitHub Issues

---

**祝錄製順利！** 🎥✨
