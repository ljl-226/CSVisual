# -*- coding: utf-8 -*-
"""labVariants.js 各主题的 JavaScript 等价实现。

单独放一个文件是为了让 add_js_variants.py 能安全注入：
这些代码块是 100~200 行的模板字符串，用编辑器插入极易和相邻语言的代码串味
（上一轮就打进过乱码字符）。改错了重跑一次脚本即可复原。

每份都必须能直接 `node xxx.js` 跑通 —— 「语法像但跑不通」的示例会教错学生。
"""

SNIPPET_POINTER = r"""    javascript: `// JS 没有指针，但「引用」的行为和 C 的指针很像：
// 传给函数的是对象本身（改到的是同一个对象），基础类型则只复制一份值。
// 另一个和指针最像的地方是闭包 —— 它会把变量「抓住」，活过函数作用域。

function mutate(obj) {
  obj.n = 99;            // 改到的是调用方那个对象
  let local = 1;         // 这个只活在函数里
  return function () {
    return local;        // 闭包抓住了 local，函数返回后依然有效
  };
}

const target = { n: 1 };
const getter = mutate(target);
console.log(target.n);        // 99  —— 引用传递
console.log(getter());        // 1   —— 闭包保留

// 值传递的对照组：基础类型只是复制一份
function tryMutateNum(x) { x = 99; }
let num = 1;
tryMutateNum(num);
console.log(num);            // 1   —— 值传递，num 没变

// 对象身份 === 就是 C 里「两个指针指向同一块内存」的比较
const a = { v: 1 };
const b = a;
const c = { v: 1 };
console.log(a === b);        // true  同一个对象
console.log(a === c);        // false 结构相同但不是同一个对象

// 「内存」的对应物就是对象本身：GC 替你管理，不用 free
const big = { data: new Array(1e5).fill(0) };
console.log(big.data.length);   // 100000
`"""

SNIPPET_MEMORY = r"""    javascript: `// JS 的内存布局是「看不见」的，但仍有对应物：
// 值类型按值存放，对象按引用存放，ArrayBuffer 才是真正连续的字节。

// 1) 固定宽度类型 = C 的结构体：一段连续的原始字节
const buf = new ArrayBuffer(8);
const i32 = new Int32Array(buf);
const f32 = new Float32Array(buf);
i32[0] = 1065353216;                      // 0x3f800000
console.log(f32[0]);                      // 1  —— 同一段内存，按 float32 读就是 1.0
console.log(buf.byteLength, i32.BYTES_PER_ELEMENT);   // 8 4

// 2) 数组是连续的，但可以「越界写」（JS 静默忽略，不像 C 会踩内存）
const arr = [1, 2, 3];
arr[10] = 99;                 // 不报错，但 length 变成 11
console.log(arr.length, arr[10]);          // 11 99
console.log(arr[5]);                       // undefined —— 空洞是 undefined，不是 0

// 3) 字节级视图：真正的「指针 + 偏移」
const bytes = new Uint8Array(4);
bytes[0] = 0xff;
console.log(bytes[0], bytes.length, bytes.byteLength);   // 255 4 4

// 4) 栈：递归太深会爆栈，等价于 C 的栈溢出
function deep(n) { return deep(n + 1); }
try {
  deep(0);
} catch (e) {
  console.log(e instanceof RangeError);    // true —— 调用栈爆了
}

// 5) 释放：不用 free，但 WeakRef 让你在必要时观察回收
const w = new WeakRef({ big: new Array(1e5).fill(0) });
console.log(w.deref() !== undefined);      // 通常 true，取决于 GC 时机
`"""

SNIPPET_OOP_CLASS = r"""    javascript: `// JS 有 class，但「封装」靠 # 私有字段 + 约定，不是编译期全面强制 ——
// 这是和 Java / C++ 差别最大的地方。

class Animal {
  #name;                      // 真正的私有字段：类外访问它会直接语法错误

  constructor(name) {
    this.#name = name;        // 只能在本类内部写
  }

  get name() { return this.#name; }   // 读方法写成 getter，用起来像属性

  speak() {                   // 父类给个默认实现
    console.log(this.#name + '：……（沉默）');
  }
}

class Dog extends Animal {
  constructor(name) { super(name); }   // 必须先调 super()，this 才能用

  speak() {                   // 覆盖父类方法（JS 无需 virtual / override 关键字）
    console.log(this.name + ' 说：汪汪');
  }
}

const d = new Dog('旺财');
d.speak();

const p = new Animal('普通动物');
p.speak();                   // 动态分派天然生效

// 鸭子类型：只要有 speak() 就能用，不需要继承
class Robot { speak() { console.log('机器人：哔哔'); } }

for (const x of [d, p, new Robot()]) {
  x.speak();                 // 三种类型统一处理
}

// 「抽象」在 JS 里没有关键字，靠约定：基类方法直接抛错
class Shape {
  area() { throw new Error('子类必须实现 area()'); }
}
class Square extends Shape {
  constructor(side) { super(); this.side = side; }
  area() { return this.side * this.side; }
}
console.log(new Square(3).area());           // 9
try { new Shape().area(); } catch (e) { console.log(e.message); }
`"""

SNIPPET_OOP_POLY = r"""    javascript: `// JS 的「多态」有两套机制，用途完全不同：
// 1) 鸭子类型 —— 靠方法名约定，结构化类型天然支持
// 2) 继承链 + super —— 用来复用实现，不是多态的前提

// 1) 鸭子类型：三个类毫无继承关系，只靠方法名就能放进同一个数组
class Dog { speak() { return '汪汪'; } }
class Cat { speak() { return '喵喵'; } }
class Robot { speak() { return '哔哔'; } }

for (const a of [new Dog(), new Cat(), new Robot()]) {
  console.log(a.speak());    // 动态分派：调用的是实际类型上的方法
}

// 2) 继承 + 抽象基类：把「必须实现」的约束写进运行期
class Shape {
  // 没有 abstract 关键字，靠调用基类实现来抛错
  area() { throw new Error(this.constructor.name + ' 必须实现 area()'); }
  describe() { return '面积 ' + this.area(); }   // 模板方法：流程固定，子类填空
}

class Rect extends Shape {
  constructor(w, h) { super(); this.w = w; this.h = h; }
  area() { return this.w * this.h; }
}

class Circle extends Shape {
  constructor(r) { super(); this.r = r; }
  area() { return Math.PI * this.r * this.r; }
}

console.log(new Rect(3, 4).describe());        // 面积 12
console.log(new Circle(1).describe());         // 面积 3.141592653589793
try { new Shape().describe(); } catch (e) { console.log(e.message); }

// 3) 需要「多继承」时用 mixin 组合，而不是硬造继承链
const withLog = (Base) => class extends Base {
  speak() {
    console.log('[log] before');
    const r = super.speak();
    console.log('[log] after');
    return r;
  }
};
class Loud { speak() { return '汪汪!'; } }
console.log(new (withLog(Loud))().speak());
`"""

SNIPPET_GENERICS = r"""    javascript: `// JS 没有泛型语法，但有三种替代机制，各自有代价：

// 1) 鸭子类型：函数靠约定工作，运行期不检查 —— 最常用，也最易出错
function first(arr) { return arr[0]; }
console.log(first([1, 2, 3]), first(['a', 'b']), first(new Set(['x'])));

// 2) 约定类型：文档里写「只接受数值数组」，但传错不报错，只会静默出 NaN
function sum(arr) {
  let s = 0;
  for (const v of arr) s += v;
  return s;
}
console.log(sum([1, 2, 3]), sum(['a', 'b']));   // 6 NaN

// 3) 运行期校验：相当于 <T extends Number>，主动挡一下
function checkedSum(arr) {
  if (!Array.isArray(arr)) throw new TypeError('需要数组');
  for (const v of arr) {
    if (typeof v !== 'number') throw new TypeError('元素必须是数字，收到 ' + typeof v);
  }
  return arr.reduce((a, b) => a + b, 0);
}
console.log(checkedSum([1, 2, 3]));
try { checkedSum(['a']); } catch (e) { console.log(e.message); }

// 4) JSDoc 写类型 + 外部工具（tsc / eslint）检查：TS 生态的常规做法
/** @param {number[]} arr @returns {number} */
function head(arr) { return arr[0]; }
console.log(head([1, 2, 3]));

// 5) 泛型最核心的价值「类型擦除」在 JS 里天然成立：
// 不管 T 是什么，运行期就是同一个函数，不会「为每个 T 生成一份代码」
console.log(head === head);     // true
`"""

SNIPPET_EXCEPTION = r"""    javascript: `// JS 的异常：throw 可以抛任意值，但只有 Error 子类带 message / stack。
// finally 一定执行 —— 和 Java 的 try-with-resources 是同一个诉求。

class AppError extends Error {
  constructor(message, code) {
    super(message);         // 必须先调 super()，否则 this 不可用
    this.name = 'AppError';
    this.code = code;
  }
}

function risky(n) {
  if (n < 0) throw new AppError('参数不能为负', 400);
  if (n === 0) throw new RangeError('除数不能为 0');   // 内置错误类型
  return 10 / n;
}

// 1) 基本用法：按类型分派（C++ 只能按类型，Java 只能按异常类，JS 两者都行）
for (const n of [2, 0, -1]) {
  try {
    console.log('结果', risky(n));
  } catch (e) {
    if (e instanceof AppError) console.log('业务错误', e.code, e.message);
    else if (e instanceof RangeError) console.log('范围错误', e.message);
    else console.log('兜底', e);
  } finally {
    console.log('finally 一定执行 n=' + n);
  }
}

// 2) 可以只有 try + finally，没有 catch
function noCatch() {
  try {
    throw new Error('没人接');
  } finally {
    console.log('没有 catch，finally 照样跑');
  }
}
try { noCatch(); } catch (e) { console.log(e.message); }

// 3) Promise 里的错误：throw 会变成 reject，必须 .catch 才拿得到。
//    try/catch 抓不到异步回调里抛的东西 —— 这是 JS 最常见的坑
Promise.reject(new AppError('异步失败', 500))
  .catch(e => console.log('Promise catch:', e.message));

// 4) 主动抛非 Error 值（不推荐）：catch 里拿不到 message / stack
try { throw '字符串'; } catch (e) { console.log(typeof e, e); }
`"""

SNIPPET_ITERATOR = r"""    javascript: `// JS 的惰性求值有两套：
// 1) 生成器函数 function* —— 每次 yield 挂起，天然惰性（对应 Python 的 yield）
// 2) 迭代器协议 { next() } —— 手写，for...of 就是靠它工作的

// 1) 生成器
function* naturals() {
  let i = 0;
  while (true) {
    const cmd = yield i++;      // 把 i 交出去，下次调用时从这一行继续
    if (cmd === 'reset') i = 0;
  }
}
const g = naturals();
console.log(g.next().value);     // 0
console.log(g.next().value);     // 1
console.log(g.next().value);     // 2
g.next('reset');
console.log(g.next().value);     // 0  —— 收到指令后重新计数

// 2) 手写迭代器：next() 返回 { value, done }，done 缺失按 false 处理
class Countdown {
  constructor(n) { this.n = n; }
  [Symbol.iterator]() { return this; }    // 返回自身即为可迭代
  next() {
    if (this.n <= 0) return { value: undefined, done: true };
    return { value: this.n--, done: false };
  }
}
console.log([...new Countdown(4)]);         // [4, 3, 2, 1]

// 3) 惰性管道：生成器串起来，中间过程一个都不落地算 —— 对应 Java Stream
function* range(n) { for (let i = 0; i < n; i++) yield i; }
function* map(it, fn) { for (const v of it) yield fn(v); }
function* filter(it, fn) { for (const v of it) if (fn(v)) yield v; }

const pipeline = filter(map(range(20), x => x * x), x => x % 2 === 1);
console.log([...pipeline].slice(0, 6));    // 只算到要用的为止：[1, 9, 25, 49, 81, 121]

// 4) 对应 C++ 的自定义 Range：同样的接口，不同的语法
console.log([...map(range(5), x => x * 2)]);   // [0, 2, 4, 6, 8]

// 5) 提前退出：take(3) 之后生成器被 return() 打断，上游根本不会跑满
function* take(it, n) {
  let i = 0;
  for (const v of it) {
    if (i++ >= n) return;
    yield v;
  }
}
let steps = 0;
function* counted() {
  for (let i = 0; i < 1000; i++) { steps++; yield i; }
}
console.log([...take(counted(), 3)], '上游只跑了', steps, '次');
`"""
