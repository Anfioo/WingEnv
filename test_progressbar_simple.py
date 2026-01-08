from prompt_toolkit.shortcuts import ProgressBar
import time

# 测试自动迭代模式
def test_auto_iteration():
    print("测试自动迭代模式:")
    pb = ProgressBar()
    for i in pb(range(10), label="任务"):
        time.sleep(0.5)

# 测试手动更新模式
def test_manual_update():
    print("\n测试手动更新模式:")
    pb = ProgressBar()
    with pb:
        task_id = pb.add_task("任务", total=10)
        for i in range(10):
            pb.update(task_id, advance=1)
            time.sleep(0.5)

if __name__ == "__main__":
    test_auto_iteration()
    test_manual_update()
