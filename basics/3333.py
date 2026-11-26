# import time
#
# import asyncio
# from unittest import result
#
#
# def query_user():
#     print("开始查询用户信息")
#     time.sleep(1)
#     print("用户信息查询用户信息")
#     return "用户信息"
# def query_order():
#     print("开始查询订单信息")
#     time.sleep(1)
#     print("订单信息查询完成")
#     return "订单信息"
# def query_llm():
#     print("开始调用大模型")
#     time.sleep(2)
#     print("大模型调用完成")
#     return "AI 回答"
# def main():
#     start=time.perf_counter()
#     user=query_user()
#     order=query_order()
#     llm=query_llm()
#     end=time.perf_counter()
#     print(user)
#     print(order)
#     print(llm)
#     print(f"总耗时{end-start:.2}秒")
# main()

# import asyncio
# from multiprocessing.connection import answer_challenge
#
#
# async def query_user():
#     print("开始查询用户信息")
#     await asyncio.sleep(1)
#     print("用户信息查询完成")
#     return "用户信息"
# async def main():
#     result=await query_user()
#     print(result)
# asyncio.run(main())
#
#
# import asyncio
# import time
# async def query_user():
#     print("开始查询用户信息")
#     await asyncio.sleep(1)
#     print("用户信息查询完成")
#     return "用户信息"
# async def query_order():
#     print("开始查询订单信息")
#     await asyncio.sleep(1)
#     print("用户信息查询完成")
#     return "订单信息"
# async def query_llm():
#     print("开始调用大模型")
#     await asyncio.sleep(2)
#     print("大模型调用完成")
#     return "AI 回答"
# async def main():
#     start=time.perf_counter()
#     user,order,answer=await asyncio.gather(query_user(),query_order(),query_llm())
#     end=time.perf_counter()
#     print(user)
#     print(order)
#     print(answer)
#     print(f"总耗时{end-start:.2f}秒")
# asyncio.run(main())

# import asyncio
# import time
# async def query_llm():
#     print("开始调用大模型")
#     await asyncio.sleep(2)
#     print("大模型调用完成")
#     return "AI 回答"
# async def query_user():
#     print("开始查询用户信息")
#     await asyncio.sleep(1)
#     print("用户信息调用完成")
#     return "用户信息"
# async def main():
#     start=time.perf_counter()
#     llm_task=asyncio.create_task(query_llm())
#     user=await query_user()
#     answer=await llm_task
#     end=time.perf_counter()
#     print(user)
#     print(answer)
#     print(f"总耗时{end-start:.2f}秒")
# asyncio.run(main())

# import asyncio
# from datetime import time
# from unittest import result
#
#
# async def query_order():
#     await asyncio.sleep(1)
#     raise ValueError("订单服务异常")
# async def query_user():
#     await asyncio.sleep(1)
#     return "用户信息"
# async def main():
#     try:
#         result=await asyncio.gather(query_order(),query_user(),)
#         print(result)
#     except ValueError as e:
#         print(f"捕获异常：{e}")
# asyncio.run(main())
#
# import asyncio
# async def query_order():
#     await asyncio.sleep(1)
#     raise ValueError("订单服务异常")
# async def query_user():
#     await  asyncio.sleep(1)
#     return "用户信息"
# async def main():
#     results=await asyncio.gather(query_order(),query_user(),return_exceptions=True)
#
#     for a in results:
#         if isinstance(a,Exception):
#             print(f"任务失败:{a}")
#         else:
#             print(f"任务成功:{a}")
# asyncio.run(main())
#
#
# import asyncio
# async def call_llm():
#     await asyncio.sleep(5)
#     return "AI 回答"
# async def main():
#     try:
#         result =await asyncio.wait_for(call_llm(),timeout=2)
#         print(result)
#     except asyncio.TimeoutError:
#         print("调用大模型超时")
# asyncio.run(main())
#
#
# import asyncio
# async def call_advanced_model():
#     print("正在调用高级模型")
#     await asyncio.sleep(5)
#     return "高级模型回答"
# async def call_backup_model():
#     print("正在调用备用模型")
#     await asyncio.sleep(1)
#     return "备用模型回答"
# async def main():
#     try:
#         result=await asyncio.wait_for(call_advanced_model(),timeout=2)
#     except asyncio.TimeoutError:
#         print("高级模型调用超市，正在调用备用模型")
#         result=await call_backup_model()
#     print(result)
# asyncio.run(main())

# import asyncio
# import time
# from threading import Semaphore
#
#
#
# async def call_llm(index:int):
#     async with semaphore:
#         print(f"任务{index}开始调用大模型")
#         await asyncio.sleep(1)
#         print(f"任务{index}调用完成")
#         return f"结果{index}"
# async def main():
#     global semaphore
#     semaphore=asyncio.Semaphore(3)
#     start=time.perf_counter()
#     tasks=[call_llm(i)for i in range(10)]
#     result=await asyncio.gather(*tasks)
#     end=time.perf_counter()
#
#     print(result)
#     print(f"总耗时{end-start:.2f}秒")
# asyncio.run(main())

import asyncio
async def generate_numbers():
    for i in range(5):
        await asyncio.sleep(0.5)
        yield i
async def main():
    async for num in generate_numbers():
        print(num)

asyncio.run(main())


import asyncio
async def stream_llm_answer(question:str):
    answer=f"你问的是{question}.这是一个模拟的大模型流式回答"
    for char in answer:
        await asyncio.sleep(0.05)
        yield char
async def main():
    async for chunk in stream_llm_answer("什么是AI Agent"):
        print(chunk,end="",flush=True)
    print()
asyncio.run(main())        

