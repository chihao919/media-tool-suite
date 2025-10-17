# 建置說明 (Build Instructions)

本文檔說明如何為 macOS 和 Windows 創建安裝檔。

## 前置需求

### 通用需求
- Python 3.7 或更高版本
- FFmpeg 已安裝並在 PATH 中可用

### macOS 建置需求
```bash
pip install py2app
```

### Windows 建置需求
```bash
pip install pyinstaller
```

## macOS 建置

### 1. 建立 .app 應用程式包

```bash
# 安裝依賴
pip install py2app

# 建置應用程式
python build_mac.py py2app

# 清理建置檔案（可選）
python build_mac.py py2app --dist-dir=dist --build-dir=build
```

建置完成後，應用程式會在 `dist/` 目錄中：
- `dist/檔案豪幫手.app` - 可執行的 macOS 應用程式

### 2. 創建 DMG 安裝檔（可選）

```bash
# 創建 DMG 檔案
hdiutil create -volname "檔案豪幫手" -srcfolder dist -ov -format UDZO "檔案豪幫手_v2.0.0.dmg"
```

## Windows 建置

### 1. 建立可執行檔

```bash
# 安裝依賴
pip install pyinstaller

# 執行建置腳本
python build_windows.py
```

這會創建：
- `dist/檔案豪幫手.exe` - 單一可執行檔
- `installer.nsi` - NSIS 安裝程式腳本

### 2. 創建安裝程式（可選）

1. 下載並安裝 [NSIS](https://nsis.sourceforge.io/)
2. 執行 NSIS 編譯器：
   ```cmd
   makensis installer.nsi
   ```

這會創建 `檔案豪幫手_2.0.0_Setup.exe` 安裝程式。

## 建置選項

### 優化建置大小

對於更小的檔案大小：

**macOS:**
```bash
python build_mac.py py2app --optimize=2 --excludes=test
```

**Windows:**
```bash
# 在 build_windows.py 中已包含優化選項
# 排除不必要的模組以減少檔案大小
```

### 包含圖示

1. 為 macOS 準備 `.icns` 檔案
2. 為 Windows 準備 `.ico` 檔案
3. 在建置腳本中取消註解圖示相關行並指定檔案路徑

## 測試建置

### macOS 測試
```bash
# 測試 .app 檔案
open dist/檔案豪幫手.app

# 或在終端中執行
./dist/檔案豪幫手.app/Contents/MacOS/檔案豪幫手
```

### Windows 測試
```cmd
# 執行可執行檔
dist\檔案豪幫手.exe
```

## 發布檢查清單

- [ ] 測試所有核心功能（轉換、分割、設定）
- [ ] 確認 FFmpeg 依賴說明清楚
- [ ] 驗證檔案關聯和圖示顯示正確
- [ ] 測試安裝和解除安裝流程
- [ ] 檢查不同作業系統版本的兼容性

## 故障排除

### 常見問題

**ModuleNotFoundError:**
- 確保所有依賴模組都在 `--hidden-import` 列表中

**檔案路徑問題:**
- 使用相對路徑並確保資源檔案包含在建置中

**FFmpeg 找不到:**
- 提醒使用者安裝 FFmpeg 並添加到 PATH

**權限問題 (macOS):**
```bash
# 如果遇到權限問題
xattr -cr dist/檔案豪幫手.app
```

**Windows 防毒軟體誤報:**
- 可能需要在防毒軟體中添加例外
- 考慮程式碼簽名（需要開發者憑證）

## 自動化建置

可以創建 GitHub Actions 或其他 CI/CD 流程來自動化建置過程：

```yaml
# .github/workflows/build.yml 範例
name: Build Applications
on: [push, release]
jobs:
  build-mac:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build macOS app
        run: python build_mac.py py2app

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Windows exe
        run: python build_windows.py
```