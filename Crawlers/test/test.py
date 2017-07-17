
import re

inputStr = "hello crifan, nihao crifan"
replacedStr = re.sub(r"hello (\w+), nihao \1", "crifanli", inputStr)
print "replacedStr=",replacedStr #crifanli