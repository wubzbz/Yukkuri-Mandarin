# 直接运行的测试
# uv run python tests/test.py

from yukkurimandarin import text_convert
from time import time

start = time()

print(text_convert("美好的一天，一心二用，一石二鸟，一款产品，一箭双雕"))
end = time()
print(end - start)

print(text_convert("朕出上联：一行征雁向南飞。"))
end2 = time()
print(end2 - end)

print(text_convert("你想不想要说不要？不，不行还是部分不会。不按照就不关心。为什么不看不行？不不不不不！"))
end3 = time()
print(end3 - end2)
