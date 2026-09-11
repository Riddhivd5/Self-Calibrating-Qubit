@echo off

cd /d C:\self-calibrating-qubit-readout

if not exist logs mkdir logs

echo ================================================== >> logs\collection.log
echo Collection started: %date% %time% >> logs\collection.log
echo ================================================== >> logs\collection.log

echo Running IQ data collection...
echo.

C:\self-calibrating-qubit-readout\.venv\Scripts\python.exe collect_data.py >> logs\collection.log 2>&1

if errorlevel 1 (
    echo.
    echo COLLECTION FAILED
    echo Collection failed: %date% %time% >> logs\collection.log
    exit /b 1
)

echo.
echo Collection succeeded.
echo Collection succeeded: %date% %time% >> logs\collection.log

echo Adding new data to Git...
git add data

git diff --cached --quiet

if errorlevel 1 (
    git commit -m "Collect IQ data %date% %time%"
)

echo Pushing to GitHub...
git push >> logs\collection.log 2>&1

if errorlevel 1 (
    echo.
    echo GITHUB PUSH FAILED
    echo GitHub push failed: %date% %time% >> logs\collection.log
    exit /b 1
)

echo.
echo GitHub push successful.
echo GitHub push successful: %date% %time% >> logs\collection.log

echo ================================================== >> logs\collection.log
echo Collection finished: %date% %time% >> logs\collection.log
echo ================================================== >> logs\collection.log

exit /b 0