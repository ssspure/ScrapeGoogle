import os

result = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "result.txt"

fresult = open(result, "w")

for i in range(0,10):
    fresult.write(str(i))
    fresult.write("\n")

fresult.flush()

fresult.close()