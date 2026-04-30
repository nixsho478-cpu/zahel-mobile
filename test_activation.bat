@echo off
echo Testing virtual environment activation...
call env_zahel\Scripts\activate.bat
echo After activation, running Python test...
python test_env.py > test_output.txt 2>&1
echo Test completed. Check test_output.txt for results.
type test_output.txt