import os

# the purpose of this script is to build the command which you wish to
# run on the startracker pi.  You can also run the built command in the
# terminal in the "New_Startracker/tests/" directory if you so desire.
# A built command would look like "./unit_test.sh -t Indoor_test_pointing 5 0".
# When running command, take out the quotes

os.chdir("New_Startracker/tests/")

num_stars = 5
serial = 0 # if running from star_tracker pi, leave as 0.

cmd = "./unit_test.sh " + my_cmd + " Indoor_test_pointing

os.system("./unit_test.sh -c Indoor_test_pointing 5 0")
# -r = recompile C code if chage the C code
# -i = lis mode
# -c = autonomous calibration mode
# -t = tracking mode
