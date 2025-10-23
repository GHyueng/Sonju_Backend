import sys
import math
totalRuntime = [0, 0, 0]
for line in sys.stdin:
    if line == "=\n":
        break
    runTime = list(map(int, line.split(' ')))
    for i in range(1, len(runTime) + 1):
        totalRuntime[-i] += runTime[-i]
for i in range(1, len(totalRuntime)):
    totalRuntime[-i - 1] += totalRuntime[-i] // 60
    totalRuntime[-i] %= 60
if totalRuntime[0] > 0:
    print("{}시간 {}분 {}초".format(totalRuntime[0], totalRuntime[1], totalRuntime[2]))
else:
    print("{}분 {}초".format(totalRuntime[1], totalRuntime[2]))
print("배속 얼마나?: ", end="")
times = float(input())
seconds = (totalRuntime[0] * 3600) + (totalRuntime[1] * 60) + totalRuntime[2]
if seconds % times == 0:
    seconds = seconds / times
    seconds = int(seconds)
else:
    seconds = seconds / times
    seconds = math.ceil(seconds)
totalRuntime[0] = seconds // 3600
seconds %= 3600
totalRuntime[1] = seconds // 60
seconds %= 60
totalRuntime[2] = seconds
if totalRuntime[0] > 0:
    print("{}시간 {}분 {}초".format(totalRuntime[0], totalRuntime[1], totalRuntime[2]))
else:
    print("{}분 {}초".format(totalRuntime[1], totalRuntime[2]))
print("ㅅㄱ")
