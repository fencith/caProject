@echo off
echo 南网102-e文件解析工具 Rust版本批量测试
echo ======================================
echo.

set SUCCESS_COUNT=0
set FAIL_COUNT=0
set TOTAL_COUNT=0

echo [测试阶段1] 102E2601目录测试
echo --------------------------
for /r "102E2601" %%f in (*.dat) do (
    set /a TOTAL_COUNT+=1
    echo Testing: %%~nxf
    target\release\efile_parser_gui.exe "%%f" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   ✓ SUCCESS
        set /a SUCCESS_COUNT+=1
    ) else (
        echo   ✗ FAILED
        set /a FAIL_COUNT+=1
    )
)
echo.

echo [测试阶段2] 20260114目录测试
echo ----------------------------
for /r "20260114" %%f in (*.dat) do (
    set /a TOTAL_COUNT+=1
    echo Testing: %%~nxf
    target\release\efile_parser_gui.exe "%%f" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   ✓ SUCCESS
        set /a SUCCESS_COUNT+=1
    ) else (
        echo   ✗ FAILED
        set /a FAIL_COUNT+=1
    )
)
echo.

echo [测试结果汇总]
echo ==============
echo 总文件数: %TOTAL_COUNT%
echo 成功数: %SUCCESS_COUNT%
echo 失败数: %FAIL_COUNT%
echo 成功率: 待计算
echo.

if %FAIL_COUNT% EQU 0 (
    echo 🎉 所有测试通过！
) else (
    echo ⚠️  有 %FAIL_COUNT% 个文件测试失败
)

echo.
echo 测试完成时间: %date% %time%
pause
