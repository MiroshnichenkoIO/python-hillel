@echo off
rem Обгортка для Windows: дозволяє запускати hello.sh подвійним кліком.
rem Windows не вміє запускати .sh сам, тому ми просимо про це bash із Git Bash.
"C:\Program Files\Git\bin\bash.exe" "%~dp0hello.sh"
pause
