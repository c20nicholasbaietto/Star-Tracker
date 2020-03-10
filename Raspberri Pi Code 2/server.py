import os

os.chdir("New_Startracker/tests/")
os.system("./unit_test.sh -c Indoor_test_pointing")
# -r = recompile C code if chage the C code
# -i = lis mode
# -c = autonomous calibration mode
# -t = tracking mode
