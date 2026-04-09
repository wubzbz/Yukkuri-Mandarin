# 直接运行的测试

from yukkurimandarin import pinyin_convert, text_convert
from time import time

start = time()

print(text_convert("不，不对，就不说不要散步了，是不是部分不正确，不会是不好不好吧。你要不要吧！对不起"))
end = time()
print(end - start)

print(text_convert("不，不对，就不说不要散步了，是不是部分不正确，不会是不好不好吧。你要不要吧！对不起"))
end2 = time()
print(end2 - end)

print(text_convert("你想不想要说不要？不，不行还是部分不会。不按照就不关心。为什么不看不行？不不不不不！"))
end3 = time()
print(end3 - end2)
