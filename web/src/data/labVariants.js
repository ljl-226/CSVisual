/**
 * 跨语言等价实现（任务四 / 任务五）
 *
 * 目的：单点学习某个概念（例如「指针与地址运算」）时，用户想立刻看到
 * 同一件事在 C / C++ / Java / Python 里分别怎么写，用来横向对比。
 *
 * 设计：
 *   - 把 33 个实验室按「概念主题」分组（THEME_OF 把 slug 映射到主题）。
 *   - 每个主题下给出若干语言的等价实现（VARIANTS）。
 *   - 切换语言时：优先取该主题在该语言下的现成实现；
 *     没有现成实现时，保留用户当前代码并提示，而不是丢内容。
 *
 * 为什么不直接按语言生成代码？
 *   自动翻译代码会产生「语法像但跑不通」的产物，学生拿去看反而学错。
 *   这里只收录人工确认能直接编译/运行的写法，缺就明说缺。
 */

/** slug -> 主题 id。同主题的实验在不同语言下讲的是同一件事。 */
const THEME_OF = {
  // 指针 / 内存
  'c-pointer': 'pointer-memory',
  'c-malloc': 'pointer-memory',
  'cpp-raii': 'pointer-memory',
  'java-object': 'pointer-memory',
  'py-class': 'pointer-memory',
  // 内存布局
  'c-struct': 'memory-layout',
  'c-array': 'memory-layout',
  'c-stack': 'memory-layout',
  // 面向对象
  'cpp-class': 'oop-class',
  'java-object': 'oop-class',
  'py-class': 'oop-class',
  // 多态 / 抽象
  'cpp-polymorphism': 'oop-polymorphism',
  'java-generic': 'oop-polymorphism',
  // 模板 / 泛型
  'cpp-template': 'generics',
  'java-generic': 'generics',
  // 集合 / 容器
  'cpp-stl': 'collection',
  'java-collection': 'collection',
  'py-list': 'collection',
  'js-array': 'collection',
  // 异常
  'java-exception': 'exception',
  'py-exception': 'exception',
  // 并发
  'java-thread': 'concurrency',
  'js-async': 'concurrency',
  // 函数 / 高阶
  'py-decorator': 'function',
  'js-array': 'function',
  // 对象 / 解构
  'js-object': 'object-literal',
  // DOM / 事件
  'js-dom': 'dom-event',
  // 前端三件套之间无等价概念，交给 LABS 自身
  'html-structure': null,
  'html-form': null,
  'html-table-list': null,
  'html-media': null,
  'html-a11y': null,
  'css-box': null,
  'css-selector': null,
  'css-flex': null,
  'css-grid': null,
  'css-responsive': null,
  'js-basics': 'type-system',
  'py-generator': 'iterator'
}

export const THEME_LABEL = {
  'pointer-memory': '指针与内存',
  'memory-layout': '内存布局与栈',
  'oop-class': '类的定义与封装',
  'oop-polymorphism': '多态与抽象',
  generics: '泛型与类型擦除',
  collection: '常用容器与集合',
  exception: '异常处理',
  concurrency: '并发与异步',
  function: '函数与高阶函数',
  'object-literal': '对象与结构',
  'dom-event': 'DOM 与事件',
  'type-system': '类型系统与相等判断',
  iterator: '迭代器与惰性求值'
}

/**
 * 主题 -> 语言 -> 等价代码。
 * 这里只放人工核对过、能直接编译/运行的实现。
 */
export const VARIANTS = {
  'pointer-memory': {
    c: `#include <stdio.h>

int main(void) {
    int a = 10;
    int *p = &a;

    printf("a 的值   = %d\\n", a);
    printf("a 的地址 = %p\\n", (void *)&a);
    printf("*p 的值  = %d\\n", *p);

    *p = 20;
    printf("改后 a   = %d\\n", a);
    return 0;
}`,
    cpp: `#include <iostream>
using namespace std;

int main() {
    int a = 10;
    int& ref = a;              // C++ 引用：指针的语法糖，不可为 null

    cout << "a 的值   = " << a << endl;
    cout << "&a 的地址= " << &a << endl;
    cout << "ref 的值 = " << ref << endl;

    ref = 20;                  // 通过引用改写 a，无需解引用
    cout << "改后 a   = " << a << endl;

    int* p = new int(42);      // 动态内存必须手动释放
    cout << "堆上值   = " << *p << endl;
    delete p;                  // C++ 里没有 free，new 配 delete
    return 0;
}`,
    java: `public class PointerMemory {
    // Java 没有指针，引用本身就是"安全了的指针"，不可为 null 解引用
    static class Box { int value = 10; }

    public static void main(String[] args) {
        Box b = new Box();

        System.out.println("b 的值   = " + b.value);
        // System.out.println("b 的地址 = " + b);   // 需 System.identityHashCode
        System.out.println("b 的标识 = " + System.identityHashCode(b));

        b.value = 20;            // 引用指向对象，改字段即改对象
        System.out.println("改后值   = " + b.value);

        // 数组在 JVM 里也是对象，arr 本质是引用
        int[] arr = new int[]{1, 2, 3};
        System.out.println("arr[1]   = " + arr[1]);
        // 垃圾回收器负责释放，C 里必须 free
    }
}`,
    python: `class Cell:
    """Python 里一切都是对象，变量只是名字绑定。"""
    def __init__(self, value):
        self.value = value

a = 10
print("a 的值 =", a)
print("a 的 id =", id(a), "（id 是内存地址，类比 C 的 &a）")

c = Cell(a)
print("c.value =", c.value, " id =", id(c))

c.value = 20                 # 改的是对象，不是变量本身
print("a 仍然是 =", a, "（a 和 c 是两个不同的名字）")

# 没有 free：对象由引用计数 + GC 回收
# 也不需要 malloc：用 [0] * n 或 list 即可
arr = [1, 2, 3]
print("arr[1] =", arr[1])
print("列表元素地址 =", [hex(id(x)) for x in arr])`,
    javascript: `// JS 没有指针，但「引用」的行为和 C 的指针很像：
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
`
  },

  'memory-layout': {
    c: `#include <stdio.h>

struct Point {          // 3 个 int，按 4 字节对齐 → 实际占 16 字节
    int x;               // 偏移 0
    int y;               // 偏移 4
    int z;               // 偏移 8  （末尾补 4 字节凑成 4 的倍数）
};

int main(void) {
    printf("sizeof(struct Point) = %zu 字节\\n", sizeof(struct Point));
    printf("offsetof x = %zu, y = %zu, z = %zu\\n",
           offsetof(struct Point, x),
           offsetof(struct Point, y),
           offsetof(struct Point, z));

    int arr[3] = {1, 2, 3};
    printf("sizeof(arr) = %zu 字节（数组不是指针！）\\n", sizeof(arr));

    int* p = arr;
    printf("sizeof(p)  = %zu 字节（指针只存一个地址）\\n", sizeof(p));

    printf("arr 和 &arr[0] 的关系：%p vs %p\\n",
           (void *)arr, (void *)&arr[0]);
    return 0;
}`,
    cpp: `#include <iostream>
#include <cstddef>
using namespace std;

struct Point {
    int x, y, z;
    // C++ 里可以给成员函数，结构体默认 public
    int sum() const { return x + y + z; }
};

class Aligned {
    char c;
    double d;        // 8 字节对齐 → 前面补 7 字节，整体占 16
};

int main() {
    cout << "sizeof(Point)    = " << sizeof(Point) << " 字节\\n";
    cout << "offsetof(Point,y)= " << offsetof(Point, y) << "\\n";
    cout << "sizeof(Aligned)  = " << sizeof(Aligned) << " 字节（对齐填充）\\n";

    int arr[3] = {1, 2, 3};
    cout << "sizeof(arr) = " << sizeof(arr) << " 字节\\n";
    int* p = arr;
    cout << "sizeof(p)  = " << sizeof(p) << " 字节\\n";
    return 0;
}`,
    java: `public class MemoryLayout {
    static class Point {
        int x;    // 对象头（mark word + 指针）之后才是字段
        int y;
        int z;

        Point(int x, int y, int z) { this.x = x; this.y = y; this.z = z; }
    }

    public static void main(String[] args) {
        Point p = new Point(1, 2, 3);
        // 没有 sizeof：JVM 屏蔽了内存布局，换来安全与可移植性
        System.out.println("字段值 = " + p.x + "," + p.y + "," + p.z);
        System.out.println("对象地址 = " + System.identityHashCode(p));

        int[] arr = {1, 2, 3};   // 数组在 JVM 里也是对象
        System.out.println("arr.length = " + arr.length);
        System.out.println("arr[1] = " + arr[1]);

        // 想看对象大小？用 JOL 库：ClassLayout.parseClass(Point.class).toPrint()
    }
}`,
    python: `import sys
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    z: int

p = Point(1, 2, 3)
print("字段值 =", p.x, p.y, p.z)

# 没有 sizeof，布局由解释器实现决定（CPython 走 PyObject）
print("字段名 =", Point.__dict__.keys())
print("sys.getsizeof(p) 只算对象头，不含引用指向的内容 =", sys.getsizeof(p))

arr = [1, 2, 3]
print("arr[1] =", arr[1], " len =", len(arr))
print("列表元素是引用（类比 C 的指针数组）:", [hex(id(x)) for x in arr])`,
    javascript: `// JS 的内存布局是「看不见」的，但仍有对应物：
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
`
  },

  'oop-class': {
    c: `/* C 没有类，用「结构体 + 函数指针」手工模拟 OOP */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Animal Animal;

typedef void (*Speak)(const Animal *self);

struct Animal {
    const char *name;
    Speak speak;          // 函数指针 = Python 的方法
};

void dog_speak(const Animal *self) {
    printf("%s 说：汪汪\\n", self->name);
}

void cat_speak(const Animal *self) {
    printf("%s 说：喵喵\\n", self->name);
}

int main(void) {
    Animal dog = {"旺财", dog_speak};
    Animal cat = {"咪咪", cat_speak};

    dog.speak(&dog);      // 显式传 this（C++ 里是隐式的）
    cat.speak(&cat);
    return 0;
}`,
    cpp: `#include <iostream>
#include <string>
using namespace std;

class Animal {
public:
    explicit Animal(string name) : name_(move(name)) {}
    virtual ~Animal() = default;

    // 虚函数：子类可覆盖，父类指针能正确调用子类实现
    virtual void speak() const { cout << name_ << "：……（沉默）" << endl; }
    string name() const { return name_; }

private:
    string name_;          // 私有成员 + 构造初始化列表 = 封装
};

class Dog : public Animal {
public:
    explicit Dog(string name) : Animal(move(name)) {}
    void speak() const override {   // override 让编译器帮你查错
        cout << name() << " 说：汪汪" << endl;
    }
};

int main() {
    Dog d("旺财");
    d.speak();

    Animal* p = &d;        // 父类指针指向子类对象（向上转型）
    p->speak();            // 虚函数分派 → 调 Dog::speak

    // 析构顺序：先子类后父类，RAII 自动完成
    return 0;
}`,
    java: `public class OopClass {
    // 字段默认私有，方法默认 public —— 封装由编译器强制
    private final String name;

    public OopClass(String name) { this.name = name; }
    public String name() { return name; }

    // 抽象类：定接口不给实现
    public abstract static class Animal {
        protected final String name;

        protected Animal(String name) { this.name = name; }
        public abstract void speak();          // 子类必须实现

        public void introduce() {             // 模板方法：统一调 speak()
            System.out.println(name + "：");
            speak();
        }
    }

    public static class Dog extends Animal {
        public Dog(String name) { super(name); }   // 必须调 super()
        @Override public void speak() { System.out.println("  汪汪"); }
    }

    public static void main(String[] args) {
        Animal d = new Dog("旺财");   // 父类引用指向子类对象
        d.introduce();                // 动态分派到 Dog.speak()
    }
}`,
    python: `class Animal:
    # __init__ 对应构造函数；self 相当于 C++ 的 this（显式传入）
    def __init__(self, name):
        self._name = name          # 单下划线 = 约定私有

    @property
    def name(self):                 # @property 把方法变成属性
        return self._name

    def speak(self):                # 默认实现，子类覆盖
        print(f"{self._name}：……（沉默）")


class Dog(Animal):
    def speak(self):                # 覆盖父类方法（Python 无需 virtual）
        print(f"{self._name} 说：汪汪")

    def __init__(self, name):
        super().__init__(name)      # 显式调父类构造


d = Dog("旺财")
d.speak()
a = Animal("普通动物")   # 父类引用指向子类对象
a.speak()                # Python 天然动态分派

# 鸭子类型：只要有 speak() 就能用，不需要继承
class Robot:
    def speak(self):
        print("机器人：哔哔")

for x in [d, a, Robot()]:
    x.speak()           # 三种类型统一处理`,
    javascript: `// JS 有 class，但「封装」靠 # 私有字段 + 约定，不是编译期全面强制 ——
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
`
  },

  'oop-polymorphism': {
    cpp: `#include <iostream>
#include <memory>
#include <vector>
using namespace std;

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;         // 纯虚函数：抽象接口
    virtual string name() const { return "Shape"; }
};

class Circle : public Shape {
    double r_;
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return 3.1415926 * r_ * r_; }
    string name() const override { return "Circle"; }
};

class Rect : public Shape {
    double w_, h_;
public:
    Rect(double w, double h) : w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
    string name() const override { return "Rect"; }
};

int main() {
    vector<unique_ptr<Shape>> shapes;      // 多态：基类指针指向派生类
    shapes.push_back(make_unique<Circle>(2));
    shapes.push_back(make_unique<Rect>(3, 4));

    double sum = 0;
    for (const auto& s : shapes) {
        // 编译期静态绑定 Shape::area，运行期动态分派到实际实现
        cout << s->name() << " 面积 = " << s->area() << endl;
        sum += s->area();
    }
    cout << "总面积 = " << sum << endl;

    // Shape s;  // 编译错误：抽象类不能实例化
    return 0;
}`,
    java: `import java.util.*;

public class OopPolymorphism {
    interface Shape {                 // 接口 = 纯抽象的 C++ 抽象类
        double area();
        default String name() { return "Shape"; }
    }

    record Circle(double r) implements Shape {   // record = 值对象 + 自动 getter
        public double area() { return Math.PI * r * r; }
        public String name() { return "Circle"; }
    }

    static class Rect implements Shape {
        final double w, h;
        Rect(double w, double h) { this.w = w; this.h = h; }
        public double area() { return w * h; }
        public String name() { return "Rect"; }
    }

    public static void main(String[] args) {
        // 多态：父类型引用/接口引用指向子类型对象
        List<Shape> shapes = new ArrayList<>();
        shapes.add(new Circle(2));
        shapes.add(new Rect(3, 4));

        double sum = 0;
        for (Shape s : shapes) {          // 动态分派
            System.out.println(s.name() + " 面积 = " + s.area());
            sum += s.area();
        }
        System.out.println("总面积 = " + sum);

        // Shape s = new Shape();  // 编译错误：接口不能实例化
    }
}`,
    python: `from abc import ABC, abstractmethod
from dataclasses import dataclass
import math


class Shape(ABC):
    """抽象基类：@abstractmethod 保证子类必须实现 area"""
    @abstractmethod
    def area(self) -> float: ...

    def name(self) -> str:
        return "Shape"


@dataclass
class Circle(Shape):
    r: float

    def area(self) -> float:
        return math.pi * self.r ** 2

    def name(self) -> str:
        return "Circle"


@dataclass
class Rect(Shape):
    w: float
    h: float

    def area(self) -> float:
        return self.w * self.h


# 多态：父类引用指向子类对象，运行期动态分派
shapes = [Circle(2), Rect(3, 4)]
total = 0
for s in shapes:
    print(f"{s.name()} 面积 = {s.area()}")
    total += s.area()
print(f"总面积 = {total}")

# Shape()  # TypeError: Can't instantiate abstract class

# 结构性子类型：只要有 area() 就算 Shape，不需显式继承
class Triangle:
    def __init__(self, b, h):
        self.b, self.h = b, h
    def area(self):
        return self.b * self.h / 2
    def name(self):
        return "Triangle"

shapes.append(Triangle(4, 5))   # 也能放进同一个列表
print(f"{shapes[-1].name()} 面积 = {shapes[-1].area()}")`,
    c: `/* C 用函数指针表实现「多态」：结构体里存一组函数指针 */
#include <stdio.h>
#include <stddef.h>

typedef struct Shape Shape;
struct Shape {
    const char *(*name)(const Shape *self);
    double (*area)(const Shape *self);
};

typedef struct { Shape base; double r; } Circle;

static const char *circle_name(const Shape *s) { (void)s; return "Circle"; }
static double circle_area(const Shape *s) {
    const Circle *c = (const Circle *)s;         // 回退到派生结构
    return 3.1415926 * c->r * c->r;
}

int main(void) {
    Circle c;
    c.base.name = circle_name;                   // 相当于设置虚表
    c.base.area = circle_area;
    c.r = 2;

    Shape *p = &c.base;                          // 父指针指向子对象
    printf("%s 面积 = %.4f\\n", p->name(p), p->area(p));
    /* 没有编译器帮你检查签名一致性，写错就是 UB —— 这就是 C++ 加 class 的理由 */
    return 0;
}`,
    javascript: `// JS 的「多态」有两套机制，用途完全不同：
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
`
  },

  generics: {
    cpp: `#include <iostream>
#include <vector>
#include <string>
using namespace std;

// 函数模板：T 由编译器推导
template <typename T>
T maxOf(const T& a, const T& b) {
    return a > b ? a : b;
}

// 类模板
template <typename T, int N>
struct Buffer {
    T data[N];
    T& operator[](int i) { return data[i]; }
    int size() const { return N; }
};

int main() {
    cout << maxOf(3, 7) << endl;              // T=int
    cout << maxOf(2.5, 1.5) << endl;         // T=double
    cout << maxOf<string>("a", "b") << endl;  // T 显式指定

    Buffer<double, 3> buf;                    // N 是非类型模板参数
    buf[0] = 1.5;
    cout << "buf.size() = " << buf.size() << ", buf[0] = " << buf[0] << endl;

    vector<int> vi{1, 2, 3};
    vector<string> vs{"a", "b"};
    for (auto& s : vs) cout << s;             // auto = C++11 起可推导类型
    return 0;
}`,
    java: `import java.util.*;

public class Generics {
    // 泛型方法
    static <T extends Comparable<T>> T maxOf(List<T> list) {
        T best = list.get(0);
        for (T x : list) if (x.compareTo(best) > 0) best = x;
        return best;
    }

    // 泛型类
    static class Box<T> {
        private T value;
        Box(T value) { this.value = value; }
        T get() { return value; }
        void set(T v) { this.value = v; }
    }

    public static void main(String[] args) {
        System.out.println(maxOf(List.of(3, 7, 2)));            // T=Integer
        System.out.println(maxOf(List.of(2.5, 1.5)));          // T=Double

        Box<String> sb = new Box<>("hello");                   // 编译期类型检查
        System.out.println(sb.get());
        // Box<Integer> bi = new Box<>("oops");                // 编译错误

        // 类型擦除：运行时看不到 Box<String>，只有 java.lang.Object
        System.out.println("运行时类型 = " + sb.getClass().getSimpleName());

        // 菱形推断
        List<Map.Entry<String, Integer>> entries = new ArrayList<>();
        entries.add(Map.entry("k", 1));
        System.out.println(entries);
    }
}`,
    python: `from typing import TypeVar, Generic, List, Dict

T = TypeVar("T")          # 类型变量（类似 C++ 的 typename T）


def max_of(items: List[T]) -> T:
    """泛型函数：用 TypeVar 约束，返回值类型与入参一致"""
    return max(items)


class Box(Generic[T]):    # Generic[T] = C++ 的 template<typename T>
    def __init__(self, value: T):
        self._value = value

    def get(self) -> T:
        return self._value

    def set(self, v: T) -> None:
        self._value = v


print(max_of([3, 7, 2]))                       # T=int
print(max_of([2.5, 1.5]))                     # T=float
print(max_of(["a", "b"]))                     # T=str

sb: Box[str] = Box("hello")                   # 注解只给 IDE 看，运行期不强校验
print(sb.get())

bs: List[Box[int]] = [Box(1), Box(2)]
print([b.get() for b in bs])

# 真实项目里更常用 Protocol（结构化子类型）或 ParamSpec
from typing import Protocol

class Sized(Protocol):
    def __len__(self) -> int: ...

def size(x: Sized) -> int:
    return len(x)

print(size([1, 2, 3]), size("abc"), size({1: 1}))   # 鸭子类型`,
    c: `/* C 没有泛型，靠宏或 void* 手写。两种都演示一下 */
#include <stdio.h>

#define MAX_OF(T, a, b) (((a) > (b)) ? (a) : (b))

typedef struct { int *data; size_t n; } IntVec;

int main(void) {
    int x = 3, y = 7;
    printf("max = %d\\n", MAX_OF(int, x, y));

    /* 手写「泛型容器」：牺牲类型安全换泛化 */
    IntVec v = {{1, 2, 3}, 3};
    printf("v[1] = %d, n = %zu\\n", v.data[1], v.n);

    /* 想存不同类型？用 union 或 void* + 手动强转 */
    void* any = &x;
    printf("any as int = %d\\n", *(int *)any);
    return 0;
}`,
    javascript: `// JS 没有泛型语法，但有三种替代机制，各自有代价：

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
`
  },

  collection: {
    cpp: `#include <iostream>
#include <vector>
#include <deque>
#include <unordered_map>
#include <string>
using namespace std;

int main() {
    // vector：连续内存 + 随机访问 O(1)，尾部 push O(1)
    vector<int> v{1, 2, 3};
    v.push_back(4);
    v.insert(v.begin() + 1, 99);          // 中间插入要搬元素 O(n)
    cout << "vector 大小 = " << v.size() << ", v[1] = " << v[1] << "\\n";

    // deque：两端都能 O(1) 插入
    deque<int> d{1, 2};
    d.push_front(0);

    // 迭代器：统一遍历容器，不暴露内部实现
    for (auto it = v.begin(); it != v.end(); ++it) cout << *it << ' ';
    cout << "\\n";

    // map 有序 O(log n)，unordered_map 哈希平均 O(1)
    unordered_map<string, int> freq;
    freq["a"]++;
    for (const auto& [k, val] : freq) {   // 结构化绑定 C++17
        cout << k << " -> " << val << "\\n";
    }
    return 0;
}`,
    java: `import java.util.*;

public class CollectionDemo {
    public static void main(String[] args) {
        // List 接口 + ArrayList 实现：面向接口编程
        List<Integer> v = new ArrayList<>(List.of(1, 2, 3));
        v.add(4);
        v.add(1, 99);                    // 中间插入 O(n)
        System.out.println("大小 = " + v.size() + ", get(1) = " + v.get(1));

        // LinkedList：两端插入 O(1)，中间 get O(n)
        Deque<Integer> d = new LinkedList<>();
        d.pushFirst(0);
        d.addLast(3);

        // 迭代器
        for (Iterator<Integer> it = v.iterator(); it.hasNext(); ) {
            System.out.print(it.next() + " ");
        }

        // 有序 Map（红黑树）vs HashMap（哈希）
        Map<String, Integer> freq = new HashMap<>();
        freq.merge("a", 1, Integer::sum);
        System.out.println(freq);

        // 不可变集合：List.of 返回的列表不可改
        List<Integer> fixed = List.of(1, 2);
        try {
            fixed.add(3);
        } catch (UnsupportedOperationException e) {
            System.out.println("不可变集合拒绝修改（和 C++ 的 const 视图类似）");
        }
    }
}`,
    python: `from collections import OrderedDict, defaultdict, deque

# list：动态数组（类比 C++ vector / Java ArrayList）
v = [1, 2, 3]
v.append(4)
v.insert(1, 99)               # 中间插入 O(n)
print("大小 =", len(v), ", v[1] =", v[1])

# deque：两端 O(1)，常作队列/栈用
d = deque([1, 2])
d.appendleft(0)

# 切片是新列表（拷贝），不是视图 —— 和 C++ 的 vector 一致
sub = v[1:3]
print("切片 =", sub, "（是新对象）")

# dict：Python 3.7+ 保证插入顺序，平均 O(1)
freq = {}
freq["a"] = freq.get("a", 0) + 1
for k, val in freq.items():
    print(k, "->", val)

# defaultdict 免去 get 判空
d2 = defaultdict(list)
for w in ["a", "b", "a"]:
    d2[w].append(1)
print("defaultdict =", dict(d2))

# OrderedDict 显式声明顺序语义（新版 dict 已有序）
print("键顺序 =", list(freq.keys()))`,
    javascript: `// Map / Set 是 ES6 新增：真正的键值结构，不受对象键类型限制
const m = new Map();
m.set("a", 1).set("b", 2);
m.set("a", (m.get("a") || 0) + 1);        // 累加
console.log("Map 大小 =", m.size, "m.get('a') =", m.get("a"));

// Set 去重
const s = new Set([1, 2, 2, 3]);
console.log("Set =", [...s], " size =", s.size);

// 遍历：Map/Set 都是可迭代的，有 for...of
for (const [k, v] of m) console.log(k, "->", v);

// 对象作为键（Map 可以，普通对象不行）
const keyObj = {};
m.set(keyObj, "对象的键");
console.log("对象键 =", m.get(keyObj));

// 注意：数组是「类数组」但性能特性不同
const arr = [1, 2, 3];
arr.push(4);                                  // 尾部 O(1)
arr.splice(1, 0, 99);                          // 中间插入 O(n)
console.log("数组 =", arr, " length =", arr.length);`,
    c: `/* C 标准库没有容器，需要自己手写。演示一个最简单的动态数组 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int *data;
    size_t size;
    size_t cap;
} Vec;

void vec_push_back(Vec *v, int x) {
    if (v->size == v->cap) {                    // 满了就扩容（翻倍）
        v->cap = v->cap ? v->cap * 2 : 4;
        v->data = realloc(v->data, v->cap * sizeof(int));
        if (!v->data) { perror("realloc"); exit(1); }
    }
    v->data[v->size++] = x;
}

int main(void) {
    Vec v = {NULL, 0, 0};
    for (int i = 1; i <= 6; i++) vec_push_back(&v, i * 10);
    for (size_t i = 0; i < v.size; i++) printf("%d ", v.data[i]);
    printf("\\n容量 = %zu, 长度 = %zu\\n", v.cap, v.size);
    free(v.data);                               // 不 free 就是内存泄漏
    return 0;
}`
  },

  exception: {
    java: `import java.io.*;

public class ExceptionDemo {
    static void risky(int n) throws IOException {   // 受检异常必须声明
        if (n == 0) throw new IOException("底层 IO 失败");
        if (n < 0) throw new IllegalArgumentException("参数不能为负");  // 非受检
        System.out.println("n = " + n + " 正常");
    }

    public static void main(String[] args) {
        // try-with-resources：等价于 C++ 的 RAII / Python 的 with，异常也保证关闭
        try (BufferedReader br = new BufferedReader(new FileReader("data.txt"))) {
            System.out.println(br.readLine());
        } catch (IOException e) {                 // 捕获受检异常
            System.err.println("读文件失败：" + e.getMessage());
        } catch (IllegalArgumentException e) {    // 更精确的在前
            System.err.println("参数错误：" + e.getMessage());
        } catch (Exception e) {                   // 兜底：别漏掉
            System.err.println("未知错误：" + e);
        } finally {
            System.out.println("无论如何都会执行");
        }

        try { risky(-1); }
        catch (RuntimeException e) { System.err.println("捕获到运行时异常：" + e.getMessage()); }

        try { risky(0); }
        catch (IOException e) { System.err.println("受检异常必须处理：" + e.getMessage()); }

        // 自定义异常
        class MyException extends RuntimeException {
            MyException(String msg) { super(msg); }
        }
        try { throw new MyException("自定义业务异常"); }
        catch (MyException e) { System.err.println(e.getMessage()); }
    }
}`,
    python: `class MyError(Exception):
    """自定义异常：继承 Exception 即可"""
    pass


def risky(n: int) -> None:
    if n == 0:
        raise MyError("底层失败")        # Python 的 raise
    if n < 0:
        raise ValueError(f"参数不能为负：{n}")   # 内置异常类型
    print(f"n = {n} 正常")


# Python 3.11+ 支持 ExceptionGroup / except*（多异常一起抛）
def risky_all():
    risky(0)     # 第一个异常就中断了 —— Python 没有 Java 的受检异常检查


# try/except/else/finally
try:
    risky(-1)
except MyError as e:
    print(f"自定义异常：{e}")
except (ValueError, TypeError) as e:      # 元组 = 多个类型
    print(f"捕获：{e}")
except Exception as e:                   # 兜底
    print(f"兜底：{e}")
else:
    print("没有异常时执行")
finally:
    print("无论如何都会执行")


# with 语句 = try-finally 的语法糖（也对应 Java 的 try-with-resources）
class Res:
    def __enter__(self):
        print("打开资源")
        return self

    def __exit__(self, exc_type, exc_val, tb):
        print("关闭资源（即使出异常也执行）")
        return False      # 返回 True 会吞掉异常


with Res() as r:
    print("使用资源中")

# 没有受检异常之分：所有异常都是 RuntimeException 的子类
# 好处是不用写 throws 声明，坏处是运行时才发现 —— 这是 Python 的取舍
risky_all()`,
    cpp: `#include <iostream>
#include <stdexcept>
#include <vector>
#include <string>
using namespace std;

// C++ 异常：抛出用 throw，捕获用 catch（按类型匹配，顺序由具体到宽泛）
class MyError : public runtime_error {
public:
    explicit MyError(const string& m) : runtime_error(m) {}
};

void risky(int n) {
    if (n < 0) throw invalid_argument("参数不能为负");   // 标准异常
    if (n == 0) throw MyError("底层失败");              // 自定义
    cout << "n = " << n << " 正常" << endl;
}

int main() {
    try {
        risky(-1);
    } catch (const invalid_argument& e) {
        cerr << "捕获参数异常：" << e.what() << endl;   // what() 取消息
    } catch (const exception& e) {                       // 兜底：所有标准异常基类
        cerr << "标准异常：" << e.what() << endl;
    } catch (...) {                                      // 兜底：非标准异常
        cerr << "未知异常" << endl;
    }

    // RAII：析构函数在栈展开时也会执行，等于自动 finally
    {
        vector<int> v{1, 2, 3};
        v.at(10);                       // at() 边界检查：抛 out_of_range
    }                                   // 即使抛异常，v 的析构也会跑，内存不泄漏

    // 手动抛出
    try {
        throw 42;                       // 可以抛任意类型（不推荐）
    } catch (int x) {
        cerr << "捕获 int：" << x << endl;
    }

    try { risky(0); }
    catch (const MyError& e) {
        cerr << "自定义异常：" << e.what() << endl;
    }

    // C++ 没有 finally 块，这是它相对 Java/Python 的一个明确劣势
    return 0;
}`,
    c: `/* C 没有异常机制，只能靠返回码或 goto + 统一清理 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

typedef enum {
    OK = 0,
    ERR_NEGATIVE,
    ERR_ZERO,
    ERR_NOMEM
} Status;

const char* status_msg(Status s) {
    switch (s) {
        case OK:           return "正常";
        case ERR_NEGATIVE: return "参数不能为负";
        case ERR_ZERO:     return "底层失败";
        case ERR_NOMEM:    return "内存不足";
        default:           return "未知错误";
    }
}

/* 返回错误码：每个调用点都要检查，容易漏 */
Status risky(int n, int* out) {
    if (n < 0) return ERR_NEGATIVE;
    if (n == 0) return ERR_ZERO;
    *out = n * 2;
    return OK;
}

int main(void) {
    int out = 0;
    Status s = risky(-1, &out);
    if (s != OK) {
        fprintf(stderr, "失败：%s (code=%d)\\n", status_msg(s), s);
    }

    /* 资源清理：没有 finally，必须手动，且出错路径最容易漏 */
    FILE* fp = fopen("data.txt", "r");
    if (!fp) {
        fprintf(stderr, "打开失败：%s\\n", strerror(errno));
        return 1;
    }
    /* 中间任何 return 都会漏掉 fclose —— 这就是 C++ RAII 要解决的问题 */
    fclose(fp);

    /* setjmp / longjmp：接近异常，但全局状态易被破坏，很少用 */
    return 0;
}`,
    javascript: `// JS 的异常：throw 可以抛任意值，但只有 Error 子类带 message / stack。
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
`
  },

  concurrency: {
    java: `import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.*;

public class ConcurrencyDemo {
    public static void main(String[] args) throws Exception {
        // 线程池：复用线程，避免每次 new Thread
        ExecutorService pool = Executors.newFixedThreadPool(4);
        CountDownLatch latch = new CountDownLatch(3);
        AtomicInteger counter = new AtomicInteger(0);

        for (int i = 1; i <= 3; i++) {
            final int id = i;
            pool.submit(() -> {
                try {
                    counter.incrementAndGet();       // 原子自增，无锁
                    System.out.println("任务 " + id + " 在 " + Thread.currentThread().getName());
                    Thread.sleep(50);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();   // 恢复中断标志
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(2, TimeUnit.SECONDS);        // 等三个任务都完成
        System.out.println("原子计数 = " + counter.get());
        pool.shutdown();                        // 优雅关闭：不再收新任务

        // synchronized：对象锁
        Object lock = new Object();
        synchronized (lock) {
            System.out.println("临界区内");
        }

        // 可重入锁 + 超时（避免死锁）
        ReentrantLock rl = new ReentrantLock();
        if (rl.tryLock(100, TimeUnit.MILLISECONDS)) {
            try { System.out.println("拿到锁"); }
            finally { rl.unlock(); }             // 必须在 finally 里释放
        }
    }
}`,
    javascript: `// JS 单线程，但事件循环让「并发」成为可能：
// 同步代码 + 异步回调 + 微任务队列

function task(id, ms) {
  return new Promise(resolve => setTimeout(() => resolve(\`任务 \${id} 完成\`), ms));
}

// Promise.all：并行等所有完成
async function runAll() {
  console.log("开始");
  const t0 = performance.now();

  const results = await Promise.all([
    task(1, 100), task(2, 50), task(3, 80)
  ]);
  console.log(results);
  console.log("总耗时 ≈", Math.round(performance.now() - t0), "ms（不是 230ms）");

  // Promise.allSettled：不会因单个失败而整体 reject
  const settled = await Promise.allSettled([
    Promise.resolve("ok"),
    Promise.reject(new Error("失败"))
  ]);
  console.log("各任务状态 =", settled.map(s => s.status));
}

// 微任务 vs 宏任务：微任务（Promise.then）先于宏任务（setTimeout）执行
console.log("1 同步");
setTimeout(() => console.log("4 宏任务 setTimeout"), 0);
Promise.resolve().then(() => console.log("3 微任务 then"));
console.log("2 同步");

runAll();

// 串行化：await 本质是「排队等」，CPU 密集任务不会因此并行
// 真并行要用 Web Worker / Worker Threads 或 Atomics
console.log("主线程继续跑，不会被 await 阻塞");`,
    python: `import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def task(id_: int, ms: int) -> str:
    time.sleep(ms / 1000)          # 模拟等待（I/O）
    return f"任务 {id_} 完成"


# 线程池：I/O 密集时线程有用；CPU 密集要用多进程
with ThreadPoolExecutor(max_workers=4) as pool:
    t0 = time.time()
    futures = [pool.submit(task, i, d) for i, d in [(1, .1), (2, .05), (3, .08)]]
    for f in as_completed(futures):
        print(f.result())
    print(f"总耗时 ≈ {time.time() - t0:.2f}s（并行，不是 0.23s）")

# 线程安全：锁
lock = threading.Lock()
counter = {"n": 0}

def worker():
    for _ in range(1000):
        with lock:                # 保护临界区
            counter["n"] += 1

ts = [threading.Thread(target=worker) for _ in range(4)]
[t.start() for t in ts]
[t.join() for t in ts]
print("计数 =", counter["n"], "（不加锁会少算）")

# asyncio：单线程协程，比线程更轻量
import asyncio

async def atask(i: int, ms: int):
    await asyncio.sleep(ms / 1000)
    return f"协程 {i} 完成"

async def main():
    t0 = time.time()
    print(await asyncio.gather(atask(1, .1), atask(2, .05)))
    print(f"协程总耗时 ≈ {time.time() - t0:.2f}s")

asyncio.run(main())

# 线程 vs 协程：协程不释放 GIL，适合高并发 I/O；
# CPU 密集用 multiprocessing.Process 绕过 GIL`,
    cpp: `#include <iostream>
#include <thread>
#include <mutex>
#include <future>
#include <chrono>
#include <vector>
using namespace std;

int main() {
    // std::thread：真正的 OS 线程
    vector<thread> pool;
    for (int i = 1; i <= 3; i++) {
        pool.emplace_back([i] {
            this_thread::sleep_for(chrono::milliseconds(50 * i));
            cout << "任务 " << i << " 在 " << this_thread::get_id() << " 完成" << endl;
        });
    }
    for (auto& t : pool) t.join();        // join 必须等，detach 后主线程结束就全死

    // mutex：保护共享数据
    int counter = 0;
    mutex mtx;
    vector<thread> ts;
    for (int i = 0; i < 4; i++) {
        ts.emplace_back([&] {
            for (int k = 0; k < 1000; k++) {
                lock_guard<mutex> lock(mtx);   // RAII 锁：作用域结束自动解锁
                counter++;
            }
        });
    }
    for (auto& t : ts) t.join();
    cout << "counter = " << counter << endl;

    // future / async：把返回值和异常打包成「将来」
    auto f = async([](int x) -> int { 
        if (x < 0) throw invalid_argument("负数");
        return x * x; 
    }, 5);
    try { cout << "平方 = " << f.get() << endl; }    // get() 阻塞并重新抛异常
    catch (const exception& e) { cout << "捕获异常：" << e.what() << endl; }

    // 单线程不代表没有并发：可以用 <future> / <coroutine> 做无锁并行
    return 0;
}`
  },

  function: {
    python: `from functools import wraps, reduce
import time
from typing import Callable, Any


# 装饰器 = 高阶函数：接收函数，返回新函数
def timer(fn: Callable) -> Callable:
    """测量函数耗时并打印"""
    @wraps(fn)                # 保留原函数名/docstring（lru_cache 就靠这个）
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:              # 用 finally 保证异常时也计时
            print(f"{fn.__name__} 耗时 {(time.perf_counter() - t0) * 1000:.2f}ms")
    return wrapper


@timer                                   # 等价于 add = timer(add)
def add(a: int, b: int) -> int:
    """两个数相加"""
    return a + b


add(1, 2)
add.__name__          # 'add'（wraps 保住了）
add.__doc__           # '两个数相加'


# 带参数的装饰器（三层）
def retry(times: int = 3):
    def deco(fn):
        @wraps(fn)
        def w(*a, **kw):
            last = None
            for i in range(times):
                try:
                    return fn(*a, **kw)
                except Exception as e:
                    last = e
                    print(f"第 {i + 1} 次失败：{e}")
            raise last
        return w
    return deco


@retry(times=2)
def flaky() -> str:
    import random
    if random.random() < 0.5:
        raise RuntimeError("随机失败")
    return "成功"


# 一等函数：函数是对象，可以传、可以返回
def compose(*fns):
    def inner(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return inner


print(compose(lambda x: x + 1, lambda x: x * 2)(3))   # (3*2)+1 = 7

# 匿名函数 + 柯里化
add5 = lambda x: add(5, x)
print(add5(10))

# 闭包：内层函数捕获外层变量
def counter_factory():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc


c = counter_factory()
print(c(), c(), c())      # 1 2 3（状态被保留）`,
    javascript: `// 函数是一等公民：能传、能返回、能当属性
function add(a, b) { return a + b; }

// 高阶函数
const twice = fn => x => fn(fn(x));
const inc = x => x + 1;
console.log(twice(inc)(3));              // 5

// 柯里化
const curried = a => b => c => a + b + c;
console.log(curried(1)(2)(3));

// 闭包：内层捕获外层变量，状态被保留
function counterFactory() {
  let n = 0;
  return function inc() { return ++n; };
}
const c = counterFactory();
console.log(c(), c(), c());              // 1 2 3

// 箭头函数没有自己的 this（继承外层）
const obj = {
  name: "obj",
  regular() { return (() => this.name)(); },   // obj（箭头继承 this）
  arrow: () => (typeof this === "undefined" ? "undefined" : "module this")
};

// 装饰器（TS / 框架里常用）
function log(target, key, desc) {
  const orig = target[key];
  target[key] = function (...args) {
    console.log(\`调用 \${key}\`);
    return orig.apply(this, args);
  };
}

class Service {
  fetch() { return "data"; }
}
log(Service.prototype, "fetch");
console.log(new Service().fetch());

// 默认参数 / 剩余参数 / 展开
const f2 = (a = 1, ...rest) => [a, rest];
console.log(f2(undefined, 1, 2, 3));
console.log(Math.max(...[1, 5, 3]));`,
    c: `/* C 函数是一等公民（函数指针），但没有闭包（不能捕获局部变量） */
#include <stdio.h>

typedef int (*BinOp)(int, int);

int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

int apply(BinOp op, int a, int b) { return op(a, b); }

/* 用结构体模拟「带上下文的高阶函数」：context 字段手工携带捕获的变量 */
typedef struct {
    int scale;                        // 相当于闭包捕获的自由变量
    int apply(int x);
} Mapper;

int scale_impl(int x) { return x * 1; }  /* 需要访问 Mapper.scale — 见下 */

/* C 的替代方案：把 context 显式传进函数 */
int map_with_scale(int value, int scale) { return value * scale; }

int main(void) {
    BinOp ops[] = {add, mul};
    const char* names[] = {"add", "mul"};
    for (int i = 0; i < 2; i++) {
        printf("%s(3,4) = %d\\n", names[i], apply(ops[i], 3, 4));
    }

    /* 柯里化要靠手工返回结构体 */
    int a = map_with_scale(5, 10);
    printf("map_with_scale(5,10) = %d\\n", a);

    /* 没有闭包：要造「记住状态」的函数，只能用 static 变量（不线程安全）
       或把状态塞进结构体指针 —— GCC 扩展的 Nested Functions 能捕获，
       但不是标准 C */
    return 0;
}`,
    cpp: `#include <iostream>
#include <functional>
#include <vector>
#include <algorithm>
using namespace std;

int add(int a, int b) { return a + b; }

// 函数指针 / std::function：函数是一等对象
int apply(int (*op)(int, int), int a, int b) { return op(a, b); }

// Lambda：可捕获外层变量的匿名函数（闭包）
int main() {
    cout << apply(add, 3, 4) << endl;

    int scale = 10;
    auto scaleIt = [scale](int x) { return x * scale; };   // 按值捕获
    cout << scaleIt(5) << endl;

    scale = 20;                          // 按值捕获：修改不影响已捕获的副本
    cout << scaleIt(5) << "（仍是 50）" << endl;

    auto scaleRef = [&scale](int x) { return x * scale; };  // 按引用捕获
    cout << scaleRef(5) << "（随 scale 变为 100）" << endl;

    // 柯里化：返回 lambda
    auto curried = [](int a) {
        return [a](int b) {
            return [a](int c) { return a + b + c; };
        };
    };
    cout << curried(1)(2)(3) << endl;

    // std::function 统一不同签名相同的可调用对象
    function<int(int)> f = [](int x) { return x * 2; };
    cout << f(21) << endl;

    // 泛型 lambda（C++14）
    auto printAll = [](auto& v) {
        for (auto& x : v) cout << x << ' ';
        cout << endl;
    };
    vector<int> nums{1, 2, 3};
    printAll(nums);

    sort(nums.begin(), nums.end(), [](int a, int b) { return a > b; });
    printAll(nums);
    return 0;
}`
  },

  'object-literal': {
    javascript: `// JS 对象字面量：最灵活的数据结构
const user = {
  name: "李嘉乐",
  age: 20,
  tags: ["前端", "算法"],
  // 方法：函数作为属性
  greet() { return \`你好，我是\${this.name}\`; },
  // 嵌套对象
  address: { city: "北京", geo: { lat: 39.9, lng: 116.4 } }
};

console.log(user.greet());
console.log(user.address.geo.lat);

// 解构：从对象里"拆"出变量
const { name, address: { city } } = user;         // 嵌套解构
const { name: alias = "匿名", age = 18 } = {};     // 重命名 + 默认值
console.log(name, city, alias, age);

// 展开：合并/复制
const defaults = { theme: "light", lang: "zh" };
const cfg = { ...defaults, lang: "en" };           // 后面的覆盖前面的
console.log(cfg);                                  // {theme:'light', lang:'en'}

// 剩余参数：把多余属性摘出来
const { theme, ...rest } = cfg;
console.log(theme, rest);                          // 'light' { lang: 'en' }

// 可选链与空值合并
console.log(user?.address?.geo?.lat ?? "未知");     // 39.9
console.log(user?.phone?.code ?? "无");            // '无'

// Map/Object 对比：键类型与顺序
const m = new Map([["a", 1], ["b", 2]]);
m.set(NaN, "NaN 可作键");   // Map 的键可以是任意值
console.log([...m.entries()]);

// 不可变更新：React/Redux 的标准做法
const user2 = { ...user, age: user.age + 1 };      // 不改原对象
console.log(user.age, "->", user2.age);`,
    python: `from dataclasses import dataclass, asdict
from typing import Optional


# dict 字面量：JS 对象的对应物（但键必须可 hash）
user = {
    "name": "李嘉乐",
    "age": 20,
    "tags": ["前端", "算法"],
    "address": {"city": "北京", "geo": {"lat": 39.9, "lng": 116.4}},
}


def greet(u):
    return f"你好，我是{u['name']}"


print(greet(user))
print(user["address"]["geo"]["lat"])

# 解构
name = user["name"]
city = user["address"]["city"]
alias = user.get("nickname", "匿名")      # 类似 JS 的 ?? 默认值
print(name, city, alias)

# 展开合并
defaults = {"theme": "light", "lang": "zh"}
cfg = {**defaults, "lang": "en"}         # ** 展开
print(cfg)                               # {'theme': 'light', 'lang': 'en'}

# 剩余：剔除某些键
theme = cfg.pop("theme")
print(theme, cfg)

# 安全访问
print(user.get("phone", {}).get("code", "无"))

# 注意：dict 的键只能是可 hash 值（str/int/tuple），
# 不能像 JS 那样直接用对象作键 → 需要 unhashable
# 错误示范：user[{"a": 1}] = 2
# 对应 JS Map 的写法：
from collections import OrderedDict
m = OrderedDict([("a", 1), ("b", 2)])
m[(1, 2)] = "元组可作键"
print(m)


# dataclass：更接近 TS interface 的静态类型写法
@dataclass
class Address:
    city: str
    lat: float


@dataclass
class User:
    name: str
    age: int
    address: Optional[Address] = None   # 可选字段


u2 = User("李嘉乐", 20, Address("北京", 39.9))
print(asdict(u2))                      # 转回 dict，方便序列化`,
    java: `import java.util.*;

public class ObjectLiteral {
    static class Address {
        final double lat;
        Address(double lat) { this.lat = lat; }
    }

    record User(String name, int age, Address address) {}   // record = 不可变数据类

    public static void main(String[] args) {
        Map<String, Object> user = new HashMap<>();   // 最接近 JS 对象字面量
        user.put("name", "李嘉乐");
        user.put("age", 20);
        user.put("tags", List.of("前端", "算法"));
        user.put("address", new Address(39.9));

        System.out.println(user.get("name"));
        System.out.println(((Address) user.get("address")).lat());

        // getOrDefault：类似 JS 的 ??
        Object code = user.getOrDefault("phone", Map.of()).getOrDefault("code", "无");
        System.out.println(code);

        // record：静态类型的不可变对象，自动有 equals/hashCode/toString
        User u = new User("李嘉乐", 20, new Address(39.9));
        System.out.println(u);
        System.out.println(u.name() + " / " + u.address().lat());

        // Map 不允许 null 键（HashMap 允许一个 null），但键类型受限
        // 任意对象作键 → 用 IdentityHashMap 或包装成单键 Map
        Map<List<String>, String> odd = new HashMap<>();
        odd.put(List.of("a"), "列表作键需要可变内容，实践中别这么用");
        System.out.println(odd);

        // Java 没有对象展开语法；变通方式是手工 copy
        Map<String, Object> copy = new HashMap<>(user);
        copy.put("age", 21);
        System.out.println(user.get("age") + " -> " + copy.get("age"));
    }
}`
  },

  'dom-event': {
    javascript: `// DOM 操作与事件：先拿到元素，再绑事件，最后改内容

document.addEventListener("DOMContentLoaded", () => {
  const box = document.getElementById("box");
  const btn = document.getElementById("btn");
  const out = document.getElementById("out");

  // 事件监听：三参数版可捕获冒泡阶段
  let n = 0;
  btn.addEventListener("click", (e) => {
    n++;
    // e.target 是真正被点的元素，e.currentTarget 是绑定的元素
    out.textContent = \`点击了 \${n} 次\`;
    e.stopPropagation();          // 阻止继续冒泡
    e.preventDefault();           // 阻止默认行为（如表单提交）
  }, false);

  // 事件委托：只给父容器绑一个监听，靠 target 分派
  // —— 动态新增的子元素不用重新绑定，这是它最大的价值
  box.addEventListener("click", (e) => {
    const item = e.target.closest(".item");
    if (!item) return;
    item.classList.toggle("active");
    out.textContent = "选中：" + item.textContent;
  });

  // 常用事件类型
  document.addEventListener("keydown", (e) => {
    if (e.key === "Enter") out.textContent = "回车了";
    if (e.ctrlKey && e.key === "Enter") console.log("Ctrl+Enter");
  });

  // 输入事件：input 实时触发，change 失焦才触发
  const search = document.getElementById("search");
  search.addEventListener("input", (e) => console.log("实时：", e.target.value));
  search.addEventListener("change", (e) => console.log("确认：", e.target.value));

  // 防抖：input 事件太频繁，用定时器合并
  let timer;
  search.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => console.log("防抖后触发一次"), 300);
  });

  // 元素创建与插入
  const li = document.createElement("li");
  li.textContent = "新建项";              // 用 textContent，别用 innerHTML 防 XSS
  li.className = "item";
  box.appendChild(li);

  // 观察尺寸变化（替代轮询）
  new ResizeObserver((entries) => {
    out.textContent = "宽度 " + Math.round(entries[0].contentRect.width);
  }).observe(box);
});`,
    python: `"""Python 里没有浏览器 DOM，但可以用同样的事件模型理解前端。

浏览器概念 → Python 对应：
    元素          ≈ 对象
    事件监听      ≈ 注册回调（add_listener）
    事件冒泡      ≈ 冒泡式调用链
    事件委托      ≈ 在外层统一分发（路由/dispatch）
    DOMContentLoaded ≈ 程序启动
"""

class Event:
    """最小事件系统"""
    def __init__(self, name):
        self.name = name
        self._handlers = []

    def add_listener(self, fn):
        self._handlers.append(fn)

    def stop_propagation(self):
        self._stopped = True

    def dispatch(self, target=None):
        self._stopped = False
        self.target = target or self          # 相当于 e.target
        for fn in self._handlers:
            if self._stopped:
                break                        # 相当于 e.stopPropagation()
            fn(self)


class Element:
    def __init__(self, tag, text=""):
        self.tag = tag
        self.text = text
        self.children = []
        self.classes = set()
        self.listeners = {}

    def class_list(self):
        return self.classes

    def add_class(self, c):
        self.classes.add(c)

    def toggle_class(self, c):
        self.classes.symmetric_difference_update({c})

    def append_child(self, el):
        self.children.append(el)

    def find(self, cls):
        """DOM 的 querySelector('.item')"""
        found = []
        for c in self.children:
            if cls in c.classes:
                found.append(c)
            found.extend(c.find(cls))
        return found

    def on(self, event, fn):
        self.listeners.setdefault(event, []).append(fn)

    def render(self, indent=0):
        cls = f' class="{" ".join(self.classes)}"' if self.classes else ""
        line = " " * indent + f"<{self.tag}{cls}>{self.text}" + (f"</{self.tag}>" if self.text else ">")
        for c in self.children:
            line += "\\n" + c.render(indent + 2)
        return line


# 组装页面
box = Element("div", "列表容器")
items = [Element("li", f"项目{i}") for i in range(1, 4)]
for it in items:
    it.add_class("item")
    box.append_child(it)

click = Event("click")
out = {"text": ""}


# 事件委托：只给 box 绑一个监听，靠 target 分派到具体 item
def on_box_click(e):
    item = next((c for c in box.children if c is e.target), None)
    if not item:
        return
    item.toggle_class("active")
    out["text"] = f"选中：{item.text}"


box.on("click", on_box_click)

# 模拟点击第 2 项
click.target = items[1]
click.dispatch(items[1])
print("选中状态 =", [i.classes for i in box.children])
print("输出区 =", out["text"])
print(box.render())`,
    java: `import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.List;

/** Java Swing：桌面端也有 DOM 类似的组件树 + 事件模型 */
public class DomEvent extends JFrame {
    private final JPanel box = new JPanel();
    private final JLabel out = new JLabel("点一下试试");
    private int n = 0;

    DomEvent() {
        super("事件模型对照");
        box.setLayout(new BoxLayout(box, BoxLayout.Y_AXIS));

        for (int i = 1; i <= 3; i++) {
            JLabel item = new JLabel("项目 " + i);
            item.setName("item");                    // 类似 class="item"
            box.add(item);
        }
        box.add(out);

        JButton btn = new JButton("按钮");
        btn.addActionListener(e -> {                // 点击事件
            n++;
            out.setText("点击了 " + n + " 次");
        });

        // 事件委托：给容器挂一个监听，子项不用各绑一个
        // 等价于前端 box.addEventListener('click', 靠 target 分派)
        box.addMouseListener(new MouseAdapter() {
            @Override public void mouseClicked(MouseEvent e) {
                out.setText("容器收到点击，坐标 " + e.getX() + "," + e.getY());
            }
        });

        // 键盘事件
        getRootPane().registerKeyboardAction(
            e -> out.setText("Ctrl+Enter"),
            KeyEvent.VK_ENTER,
            InputEvent.CTRL_DOWN_MASK);

        // 输入事件：实时 vs 确认
        JTextField field = new JTextField(18);
        field.addActionListener(e -> out.setText("确认：" + field.getText()));

        JPanel north = new JPanel();
        north.add(btn);
        north.add(field);
        add(north, BorderLayout.NORTH);
        add(box, BorderLayout.CENTER);
        setSize(380, 240);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new DomEvent().setVisible(true));
    }
}`,
    c: `/* C 没有 DOM，但有同样两个核心概念：回调函数 + 事件循环。
   GUI 库（GTK / Win32）就是靠「注册回调 + 派发事件」实现 DOM 模型的。 */
#include <stdio.h>

/* ---------- 事件系统 ---------- */
typedef struct EventListener EventListener;
typedef struct {
    const char *type;
    void (*handler)(const char *type, void *data, void *user);
    void *user;
} Listener;

#define MAX_LISTENERS 8
static Listener listeners[MAX_LISTENERS];
static int listener_count = 0;

void add_listener(const char *type, void (*h)(const char*, void*, void*), void *user) {
    if (listener_count >= MAX_LISTENERS) return;
    listeners[listener_count++] = (Listener){type, h, user};
}

/* 派发：遍历监听器，类型匹配就调 —— 相当于 addEventListener + 冒泡 */
void dispatch(const char *type, void *data) {
    printf("dispatch(%s)\\n", type);
    for (int i = 0; i < listener_count; i++) {
        if (listeners[i].type && strcmp(listeners[i].type, type) == 0) {
            listeners[i].handler(type, data, listeners[i].user);
        }
    }
}

/* ---------- 组件树：类似 DOM ---------- */
typedef struct Node {
    const char *tag;
    const char *text;
    int n_children;
    struct Node *children[4];
} Node;

Node* node_new(const char *tag, const char *text) {
    Node *n = calloc(1, sizeof(Node));
    n->tag = tag; n->text = text;
    return n;
}

void append_child(Node *parent, Node *child) {
    if (parent->n_children < 4) parent->children[parent->n_children++] = child;
}

/* querySelector('.item') 的简化版：按 tag 查 */
Node* query_by_tag(Node *root, const char *tag) {
    if (strcmp(root->tag, tag) == 0) return root;
    for (int i = 0; i < root->n_children; i++) {
        Node *found = query_by_tag(root->children[i], tag);
        if (found) return found;
    }
    return NULL;/* C 没有 null，得显式返回 */
}

static void on_click(const char *type, void *data, void *user) {
    Node *target = (Node *)data;
    printf("  监听到 %s：节点 <%s> %s\\n", type, target->tag, target->text);
}

int main(void) {
    Node *box = node_new("div", "列表容器");
    for (int i = 1; i <= 3; i++) {
        char buf[32];
        snprintf(buf, sizeof buf, "项目 %d", i);
        append_child(box, node_new("li", buf));
    }

    add_listener("click", on_click, NULL);

    /* 事件委托：给容器派发，handler 自己去定位真实 target */
    dispatch("click", box);
    dispatch("click", query_by_tag(box, "li"));

    printf("组件树:\\n<%s>\\n", box->tag);
    for (int i = 0; i < box->n_children; i++) {
        printf("  <%s>%s</%s>\\n", box->children[i]->tag,
               box->children[i]->text, box->children[i]->tag);
    }
    return 0;
}`
  },

  /* ---- 类型系统与相等判断：JS 的 === / null / NaN 在别的语言里怎么落地 ---- */
  'type-system': {
    javascript: `// ---- 声明方式：let 可变 / const 锁绑定但对象内容仍可改 ----
let count = 0;
const PI = 3.14159;
const user = { name: "Tom" };
user.name = "Jerry";        // const 锁的是绑定，不是内容

// ---- 原始类型：typeof 一览 ----
console.log(typeof "abc");       // string
console.log(typeof 42);          // number
console.log(typeof true);        // boolean
console.log(typeof undefined);   // undefined
console.log(typeof null);        // object  ← 历史遗留 bug
console.log(typeof Symbol());    // symbol
console.log(typeof 123n);        // bigint

// ---- 相等判断：== 隐式转换，=== 严格 ----
console.log(1 == "1");           // true   ← 隐式转换，应避免
console.log(1 === "1");          // false
console.log(null == undefined);  // true   ← 只有 == 认为相等
console.log(null === undefined); // false

// NaN 不等于任何值，包括它自己
console.log(NaN === NaN);             // false
console.log(Number.isNaN(NaN));       // true  ← 正确判断方式

// ---- 六种假值 ----
const falsy = [false, 0, "", null, undefined, NaN];
console.log(falsy.filter(v => !v).length);  // 6
console.log([] ? "真" : "假");              // 真 —— 空数组是对象`,
    python: `# Python 没有 null 而叫 None，也没有单独的 undefined。
# 未赋值的变量其实就是一个内置的 Undefined 哨兵对象。

from typing import Optional, Any

# ---- 声明方式：变量无需声明类型，约定用 _ 表示「不变」 ----
count = 0                       # 可重新赋值
PI = 3.14159                    # 惯例上不再改，但不是真正的 const
user = {"name": "Tom"}          # dict 同样能就地改

# ---- 类型判断：用 type() / isinstance()，不用 typeof ----
print(type("abc"))              # <class 'str'>
print(type(42))                 # <class 'int'>
print(type(3.14))               # <class 'float'>
print(type(True))               # <class 'bool'>
print(type(None))               # <class 'NoneType'>  ← 相当于 JS 的 null
print(type(b"x"))                # <class 'bytes'>

# ---- 相等判断：== 对多数类型就是严格比较，没有隐式转换 ----
print(1 == 1.0)                 # True  ← 数值相等，不是类型相等
print(1 == "1")                 # False ← 永远不会像 JS 那样得到 True
print(None == None)             # True
print(None == False)            # False ← 不会因为假值而误判

# NaN：同样不等于自身
nan = float("nan")
print(nan == nan)               # False
print(nan != nan)               # True   ← Python 判断 NaN 的惯用写法

# ---- 真假判断：容器为空也是假值（这点和 JS 相反）----
print(bool(0), bool(""), bool(None), bool([]), bool({}))
# False False False False False ← 空列表 / 空字典都是假
print(bool([1]), bool("0"))      # True True  ← 注意 "0" 是非空字符串`,
    java: `public class TypeSystem {
    public static void main(String[] args) {
        // ---- 声明方式：类型写死在声明里，final 相当于 const ----
        int count = 0;
        final double PI = 3.14159;
        final String[] user = { "Tom" };
        user[0] = "Jerry";              // final 锁引用，不锁数组内容（同 JS const）

        // ---- 类型判断：instanceof / getClass()，没有 typeof ----
        System.out.println("abc".getClass().getSimpleName());   // String
        System.out.println(Integer.valueOf(42).getClass().getSimpleName()); // Integer
        System.out.println(Boolean.TRUE.getClass().getSimpleName());       // Boolean
        System.out.println(Double.valueOf(1.5).getClass().getSimpleName()); // Double
        // 没有 null 这个「类型」：null 是引用变量的特殊值
        String nothing = null;
        System.out.println(nothing == null);                     // true

        // ---- 相等判断：== 比较引用 / 基本类型值，永远不会隐式转换 ----
        System.out.println(1 == 1.0);       // true  ← 数值相等
        System.out.println(1 == "1");      // 编译不过：类型不兼容
        System.out.println(nothing == null); // true  ← 必须用 ==

        // 浮点比较：不要用 ==，用容差
        double a = 0.1 + 0.2, b = 0.3;
        System.out.println(a == b);                       // false！
        System.out.println(Math.abs(a - b) < 1e-9);       // true   ← 正确做法

        // ---- JavaScript 语义对照 ----
        // JS: NaN === NaN 为 false  →  Java 里双精度 NaN 用 == 也是 false，
        //    所以同样不能靠 == 判断，惯用 Double.isNaN(a)
        double nan = Double.NaN;
        System.out.println(nan == nan);                   // false
        System.out.println(Double.isNaN(nan));            // true
        // JS: [] 是真值（对象）   →  Java 没有真值判断，集合要自己判空
        System.out.println(java.util.Arrays.asList().isEmpty()); // true
    }
}`,
    cpp: `#include <iostream>
#include <string>
#include <vector>
#include <optional>

int main() {
    // ---- 声明方式：类型 + const 限定符 ----
    int count = 0;
    const double PI = 3.14159;
    const std::string user = "Tom";
    // user = "Jerry";             // 编译不过：const 变量整个锁死
    std::string name = "Tom";
    name = "Jerry";                // 想改就一开始别加 const

    // ---- 类型判断：typeid / decltype，没有 typeof ----
    std::cout << typeid(std::string).name() << "\\n";    // std::basic_string...
    std::cout << typeid(int).name() << "\\n";            // int
    std::cout << typeid(double).name() << "\\n";         // double
    // C++ 没有 null 这个「值」：用 nullptr（指针）或 std::nullopt（optional）
    int* p = nullptr;

    // ---- 相等判断：类型不兼容时连编译都过不去 ----
    std::cout << (1 == 1.0) << "\\n";        // true  ← 数值相等
    // std::cout << (1 == "1");             // 编译错误：没有 operator==(int, const char*)
    std::cout << (p == nullptr) << "\\n";    // true  ← 相当于 JS 的 == null

    // 浮点：不要用 ==，IEEE 754 舍入让 0.1+0.2 != 0.3
    double a = 0.1 + 0.2, b = 0.3;
    std::cout << std::boolalpha << (a == b) << "\\n";                 // false
    std::cout << (std::abs(a - b) < 1e-9) << "\\n";                  // true
    std::cout << std::isnan(a * 0.0 / 0.0 == a ? 0.0 : 1.0) << "\\n";

    // 容器空判断：相当于 JS 里「空数组是真值」的坑，这里必须显式判
    std::vector<int> xs;
    std::cout << xs.empty() << "\\n";         // true
    // JS: typeof null === "object"  →  C++ 里没有这个历史 bug
    return 0;
}`,
    c: `#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

int main(void) {
    /* ---- 声明方式：类型在前，const 限定符修饰不可改的变量 ---- */
    int count = 0;
    const double PI = 3.14159;
    const char* user = "Tom";
    /* user = "Jerry"; */          /* 编译不过：const 指针不可重新赋值 */

    /* ---- 类型判断：没有 typeof，运行时用 typeid（需 RTTI），编译期靠编译器 ---- */
    printf("sizeof(int) = %zu\\n", sizeof(int));
    printf("sizeof(double) = %zu\\n", sizeof(double));
    printf("sizeof(void*) = %zu\\n", sizeof(void*));

    /* ---- 空值：C 用 NULL（整数 0 转的指针），永远用 == 比，不是函数调用 ---- */
    int* p = NULL;
    if (p == NULL) printf("p == NULL\\n");            // true
    /* 千万不要写 if (p) 来判空：能跑但语义不明确，显式和 NULL 比较更好 */
    if (p) { /* 真 */ } else { printf("p 为空\\n"); }

    /* ---- 相等判断：类型不兼容直接编译错误 ---- */
    printf("%d\\n", 1 == 1);            // 1
    /* printf("%d", 1 == "1"); */      /* 编译错误：指针和 int 比较 */
    /* 字符串比内容必须用 strcmp，不能用 ==（== 比的是地址）*/
    char a[] = "hello", b[] = "world";
    printf("a == b ? %d\\n", a == b);              // 0（地址不同）
    printf("strcmp(a,b) = %d\\n", strcmp(a, b));   // 负数（内容不同）

    /* ---- 布尔假值：C 里 0 是假，非 0 都是真，没有 JS 那么多假值 ---- */
    int zero = 0;
    printf("if(zero) 不会进；if(!zero) 会进\\n");
    if (!zero) printf("!0 == 1\\n");

    /* ---- 浮点：不要用 ==，0.1+0.2 != 0.3 ---- */
    double x = 0.1 + 0.2, y = 0.3;
    printf("x == y ? %d\\n", x == y);                       /* 0 */
    printf("fabs(x-y) < 1e-9 ? %d\\n", fabs(x - y) < 1e-9);  /* 1 */
    double nan = NAN;
    printf("nan == nan ? %d\\n", nan == nan);               /* 0，和 JS 一样 */
    printf("isnan(nan) ? %d\\n", isnan(nan));               /* 1，等价 Number.isNaN */
    return 0;
}`
  },

  /* ---- 迭代器与惰性求值：Python 生成器 ↔ JS 生成器 ↔ C++ 惰性视图 ---- */
  iterator: {
    python: `def fib(n):
    """生成器：用 yield 逐个产出，调用时才真正开始执行"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 生成器对象不是列表，不能 len() / 索引，只能迭代
g = fib(10)
print(next(g), next(g))            # 0 1
print(list(fib(10)))                # 消耗掉生成器 → [0,1,1,2,3,5,8,13,21,34]
# print(len(g))                    # TypeError：没有长度

# ---- 生成器表达式：像列表推导，但惰性求值 ----
squares_list = [x * x for x in range(5)]      # 立刻算完，5 个元素
squares_gen  = (x * x for x in range(5))      # 什么都不算，等着被取
print(type(squares_gen))                      # <class 'generator'>

# ---- 无限序列：惰性的好处，想取多少取多少 ----
def naturals():
    i = 0
    while True:
        yield i
        i += 1

it = naturals()
print([next(it) for _ in range(5)])           # [0,1,2,3,4]

# ---- 惰性表达式适合做管道式处理 ----
data = [1, 2, 3, 4, 5, 6, 7, 8]
total = sum(x * x for x in data if x % 2 == 0)  # 只算偶数的平方
print(total)                                    # 4+16+36+64 = 120`,
    javascript: `// ---- 生成器函数：function* + yield，与 Python 生成器同构 ----
function* fib(n) {
    let a = 0, b = 1;
    for (let i = 0; i < n; i++) {
        yield a;         // 产出并挂起，下次 next() 从这里继续
        [a, b] = [b, a + b];
    }
}

// 生成器对象只能迭代，不能取长度 / 索引
const g = fib(10);
console.log(g.next().value, g.next().value);  // 0 1
console.log([...fib(10)]);                    // 消耗掉 → [0,1,1,2,3,5,8,13,21,34]
// console.log(g.length);                     // undefined

// ---- for...of：最直接的消费方式 ----
for (const x of fib(5)) process.stdout.write(x + " ");   // 0 1 1 2 3

// ---- 生成器函数表达式：任意可迭代对象的工厂 ----
const make = function* () { yield 1; yield 2; };
console.log([...make()]);                    // [1, 2]

// ---- 无限序列：惰性让它想算多少算多少 ----
function* naturals() {
    let i = 0;
    for (;;) { yield i++; }     // 无限循环靠 yield 随时能停
}
const it = naturals();
console.log([...Array(5)].map(() => it.next().value));   // [0,1,2,3,4]

// ---- 惰性管道：跟 Python 生成器表达式一个思路 ----
const data = [1, 2, 3, 4, 5, 6, 7, 8];
// function* 而不是立即执行，筛选与平方都在取值时才发生
function* squareEvens(arr) {
    for (const x of arr) if (x % 2 === 0) yield x * x;
}
const total = [...squareEvens(data)].reduce((a, b) => a + b, 0);
console.log(total);                       // 4+16+36+64 = 120

// ---- async 生成器：await 与 yield 叠加（ES2018）----
async function* asyncIds() {
    yield 1;
    await new Promise(r => setTimeout(r, 0));
    yield 2;
}
(async () => {
    for await (const v of asyncIds()) console.log("async", v);  // async 1 / async 2
})();`,
    java: `import java.util.*;
import java.util.stream.*;

// Java 没有 yield 关键字，但有「惰性」的两种等价物：
// 1) Iterator（与 Iterable 的 for-each 配合）
// 2) Stream（惰性求值 + 声明式管道，最接近 Python 生成器表达式）

public class IteratorDemo {
    static Iterator<Integer> fib(int n) {
        return new Iterator<>() {
            int a = 0, b = 1, i = 0;
            public boolean hasNext() { return i < n; }
            public Integer next() {
                int r = a;
                a = b; b = r + b; i++;
                return r;
            }
        };
    }

    public static void main(String[] args) {
        // ---- Iterator：逐个取，没有长度概念（和生成器一样）----
        Iterator<Integer> it = fib(10);
        System.out.println(it.next() + " " + it.next());        // 0 1
        System.out.println(it.hasNext());                       // true
        // System.out.println(it.length());                     // 编译错误

        List<Integer> list = new ArrayList<>();
        it.forEachRemaining(list::add);
        System.out.println(list);                              // [0,1,1,2,3,5,8,13,21,34]

        // ---- for-each：编译器把 Iterator 语法糖化掉 ----
        StringBuilder sb = new StringBuilder();
        for (int x : fib(5)) sb.append(x).append(' ');
        System.out.println(sb);                                // 0 1 1 2 3

        // ---- Stream：真正的惰性管道，不加 collect 就一个都不会算 ----
        IntStream naturals = IntStream.iterate(0, i -> i + 1);
        System.out.println(naturals.limit(5).boxed().collect(Collectors.toList()));
        // [0, 1, 2, 3, 4]   ← limit 让无限流只算到第 5 个

        int[] data = { 1, 2, 3, 4, 5, 6, 7, 8 };
        int total = Arrays.stream(data)
                .filter(x -> x % 2 == 0)     // 惰性：逐元素过一遍
                .map(x -> x * x)
                .sum();
        System.out.println(total);                          // 120

        // 求和前什么都不执行，打印才知道它算过
        IntStream lazy = Arrays.stream(data).peek(x -> System.out.println("visit " + x));
        System.out.println("还没开始算");
        System.out.println(lazy.sum());
    }
}`,
    cpp: `#include <iostream>
#include <vector>
#include <numeric>
#include <iterator>

// C++20 的 generator（C++23 才是标准 coroutine）。
// 在此之前，等价物是「返回容器的函数 + 惰性做不到」，或者手写迭代器。
// 这里用三种写法演示：索引器 / 自定义迭代器 / 惰性 std::views

template <typename T>
struct Range {
    T begin_value, end_value;
    // input_iterator 概念：让 for (int x : r) 能工作
    struct It {
        T cur;
        bool operator!=(const It& o) const { return cur != o.cur; }
        It& operator++() { ++cur; return *this; }
        T operator*() const { return cur; }
    };
    It begin() { return { begin_value }; }
    It end()   { return { end_value }; }
};

int main() {
    // ---- 索引器 + accumulate：最朴素的「逐个产出」----
    std::vector<int> f(10);
    std::iota(f.begin(), f.end(), 0);
    for (int i = 1; i < 10; i++) f[i] = f[i - 1] + f[i - 2];
    int sum = std::accumulate(f.begin(), f.begin() + 5, 0);
    std::cout << sum << "\\n";            // 0+1+1+2+3 = 7

    // ---- 自定义 Range：像 Python 的 range 一样，for 的时候才产生元素 ----
    for (int x : Range<int>{0, 5}) std::cout << x << ' ';
    std::cout << "\\n";                    // 0 1 2 3 4
    // 没有长度？不对：Range 本身就是惰性容器，但元素随时可重算

    // ---- 无限序列：函数返回状态机，靠调用推进（最近似的「惰性」）----
    auto naturals = [i = 0]() mutable { return i++; };
    int picked[5];
    for (auto& p : picked) p = naturals();
    for (int p : picked) std::cout << p << ' ';
    std::cout << "\\n";                    // 0 1 2 3 4

    // ---- C++20 起有 std::views 管道，能写出接近 Python 生成器表达式的东西 ----
    // 下面这行需要 C++20：把偶数平方求和
    // auto total = data | std::views::filter([](int x){ return x % 2 == 0; })
    //                    | std::views::transform([](int x){ return x * x; });
    // int total = std::accumulate(total.begin(), total.end(), 0);

    // 标准做法仍是算法组合（注意：这些是 eager 的，不是惰性）
    std::vector<int> data = {1,2,3,4,5,6,7,8};
    int total = 0;
    for (int x : data) if (x % 2 == 0) total += x * x;
    std::cout << total << "\\n";           // 120
    return 0;
}`,
    c: `#include <stdio.h>

/* C 没有生成器，也没有一等公民的迭代器协议。
   最接近「惰性产出」的做法是：把状态藏进结构体，靠函数指针当 continuation，
   调用方显式调 next() 推进。 */

typedef struct { int cur, end; } Iter;

Iter iter_range(int lo, int hi) { return (Iter){ lo, hi }; }
int  iter_has_next(Iter it) { return it.cur < it.end; }
Iter iter_next(Iter it) { it.cur++; return it; }   /* 按值传递 → 天然不可变状态 */
int  iter_value(Iter it) { return it.cur; }

typedef struct { int a, b, n, i; } Fib;
/* 返回 0 表示结束，非 0 表示还有值，*out 带出本次产出的数 */
int fib_next(Fib *f, int *out) {
    if (f->i >= f->n) return 0;
    *out = f->a;
    int t = f->a + f->b; f->a = f->b; f->b = t; f->i++;
    return 1;
}

int main(void) {
    /* ---- 用 while 消费迭代器：等价于 Python 的 for x in range(5) ---- */
    int acc = 0;
    for (Iter it = iter_range(0, 5); iter_has_next(it); it = iter_next(it))
        printf("%d ", iter_value(it));              /* 0 1 2 3 4 */
    printf("\\n");

    /* ---- 斐波那契：状态在结构体里，调用方负责推进 ---- */
    Fib f = { 0, 1, 10, 0 };
    int v, cnt = 0;
    while (fib_next(&f, &v)) { printf("%d ", v); if (++cnt == 10) break; }
    printf("\\n");                                  /* 0 1 1 2 3 5 8 13 21 34 */

    /* ---- 惰性管道：这里只能靠把「筛选函数」和「元素」分开传，
           求值时机仍然由调用方决定 ---- */
    int data[] = { 1, 2, 3, 4, 5, 6, 7, 8 };
    int total = 0;
    for (unsigned i = 0; i < sizeof data / sizeof *data; i++)
        if (data[i] % 2 == 0) total += data[i] * data[i];
    printf("%d\\n", total);                         /* 120 */
    return 0;
}`
  }
}

/** 某个实验在某种语言下是否有等价实现 */
export function hasVariant(slug, lang) {
  const theme = THEME_OF[slug]
  if (!theme) return false
  return !!(VARIANTS[theme] && VARIANTS[theme][lang])
}

/**
 * 取等价实现。
 * @returns {{code:string, theme:string, label:string}|null}
 */
export function getVariant(slug, lang) {
  const theme = THEME_OF[slug]
  if (!theme) return null
  const group = VARIANTS[theme]
  if (!group || !group[lang]) return null
  return { code: group[lang], theme, label: THEME_LABEL[theme] || '等价实现' }
}

/** 某个实验支持切换的语言列表（不含它本来的语言） */
export function availableLangsFor(slug) {
  const theme = THEME_OF[slug]
  if (!theme) return []
  return Object.keys(VARIANTS[theme] || {})
}

/** 主题 id，Web 三件套返回 null（前端三件套之间无等价概念） */
export function themeOf(slug) {
  return THEME_OF[slug] || null
}

export default { THEME_OF, THEME_LABEL, VARIANTS, hasVariant, getVariant, availableLangsFor, themeOf }