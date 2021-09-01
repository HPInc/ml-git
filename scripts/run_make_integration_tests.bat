xcopy "%SystemRoot%\System32\OpenSSH" "%AppData%\OpenSSH\" /h /i /c /k /e /r /y
set PATH=%PATH%;%AppData%\OpenSSH\
make test.integration