# MTK Water Mark Generator Tool

Only for Internal to generate the watermark header file.

## How to build

```powershell
pyinstaller -F -w -i .\favicon.ico --version-file .\.version .\WaterMarkGenerator.py
```