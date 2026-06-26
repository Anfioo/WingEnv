import { useState } from "react";

// 定义类型
interface User {
  name: string;
  age: number;
}

export default function TestPage() {
  // TS 状态
  const [count, setCount] = useState<number>(0);
  const [user, setUser] = useState<User>({
    name: "WingEnv",
    age: 22,
  });

  // 事件函数
  function addCount() {
    setCount((prev) => prev + 1);
  }

  function changeName() {
    setUser((prev) => ({ ...prev, name: "Anfioo" }));
  }

  return (
    <div className="p-8">
      <h1 className="mb-6 text-2xl font-bold">TSX 基础演示页面</h1>

      {/* 数字计数器 */}
      <section className="mb-6">
        <h3 className="mb-2 text-lg font-semibold">计数器：{count}</h3>
        <button
          onClick={addCount}
          className="bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm transition-colors hover:opacity-90"
        >
          点我 +1
        </button>
      </section>

      {/* 对象数据渲染 */}
      <section className="mb-6">
        <h3 className="mb-2 text-lg font-semibold">用户信息</h3>
        <p className="text-muted-foreground">姓名：{user.name}</p>
        <p className="text-muted-foreground mb-2">年龄：{user.age}</p>
        <button
          onClick={changeName}
          className="bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm transition-colors hover:opacity-90"
        >
          修改姓名
        </button>
      </section>

      {/* 列表循环 TSX */}
      <section>
        <h3 className="mb-2 text-lg font-semibold">列表渲染</h3>
        {[1, 2, 3, 4, 5].map((item) => (
          <div key={item} className="text-muted-foreground py-1">
            列表项 {item}
          </div>
        ))}
      </section>

      {/*<button*/}
      {/*    onClick={window.location.href='/settings'}*/}
      {/*    className="bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm transition-colors hover:opacity-90"*/}
      {/*>*/}
      {/*    href*/}
      {/*</button>*/}
    </div>
  );
}
