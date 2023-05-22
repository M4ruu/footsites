import random
import asyncio
 
# coroutine run in the background
async def task(number):
    # generate a random value between 0 and 10
    value = random.random() * 10.0
    # suspend for some time
    await asyncio.sleep(value)
    # report done
    print(f'>Task {number} done')
 
# main coroutine
async def main():
    # start many background tasks
    for i in range(20):
        asyncio.create_task(task(i))
    # allow tasks to start
    await asyncio.sleep(0)
    # get a set of all running tasks
    all_tasks = asyncio.all_tasks()
    # get the current tasks
    current_task = asyncio.current_task()
    # remove the current task from the list of all tasks
    # all_tasks.remove(current_task)
    # report a message
    print(f'Main waiting for {len(all_tasks)} tasks...')
    # suspend until all tasks are completed
    await asyncio.wait(all_tasks)
 
# run the asyncio program
asyncio.run(main())