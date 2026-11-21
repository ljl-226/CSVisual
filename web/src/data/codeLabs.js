/**
 * 代码实验室：语言定义 + 智能提示词典 + 内置示例
 * 编辑器为自研零依赖实现，提示数据按语言组织，支持关键字/标准库函数/代码片段补全。
 * kind: kw=关键字  func=函数(带签名)  type=类型  snip=代码片段  var=标识符
 */

const C_KEYWORDS = ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'inline', 'int', 'long', 'register', 'restrict', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while', 'define', 'include', 'ifdef', 'endif'];
const CPP_KEYWORDS = C_KEYWORDS.concat(['bool', 'catch', 'class', 'constexpr', 'delete', 'explicit', 'friend', 'mutable', 'namespace', 'new', 'noexcept', 'nullptr', 'operator', 'private', 'protected', 'public', 'template', 'this', 'throw', 'try', 'typename', 'using', 'virtual', 'auto', 'override', 'final']);
const JAVA_KEYWORDS = ['abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while', 'record', 'var', 'yield'];
const PY_KEYWORDS = ['and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield', 'self'];

/* ---------- Web 前端三件套 ---------- */
// HTML：标签名 + 属性名。补全时按标签名给出成对标签，写页面时最省事
const HTML_KEYWORDS = [
  'html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style',
  'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table', 'thead', 'tbody',
  'tr', 'th', 'td', 'form', 'label', 'input', 'button', 'select', 'option',
  'textarea', 'header', 'nav', 'main', 'section', 'article', 'aside', 'footer',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'hr', 'strong', 'em', 'code', 'pre',
  'class', 'id', 'style', 'src', 'href', 'alt', 'type', 'name', 'value',
  'placeholder', 'disabled', 'checked', 'required', 'target', 'rel', 'lang', 'charset'
];
// CSS：属性名 + 常见取值关键字
const CSS_KEYWORDS = [
  'color', 'background', 'background-color', 'background-image', 'border', 'border-radius',
  'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'width', 'height', 'max-width', 'min-width', 'max-height', 'min-height',
  'display', 'position', 'top', 'right', 'bottom', 'left', 'z-index',
  'flex', 'flex-direction', 'flex-wrap', 'justify-content', 'align-items', 'align-self',
  'gap', 'row-gap', 'column-gap', 'grid', 'grid-template-columns', 'grid-template-rows',
  'font', 'font-size', 'font-weight', 'font-family', 'line-height', 'text-align',
  'text-decoration', 'letter-spacing', 'white-space', 'overflow', 'opacity',
  'box-shadow', 'text-shadow', 'transition', 'transform', 'animation', 'cursor',
  'box-sizing', 'visibility', 'outline', 'content', 'filter', 'backdrop-filter',
  'flex', 'grid', 'block', 'inline-block', 'inline', 'none', 'absolute', 'relative',
  'fixed', 'sticky', 'static', 'center', 'space-between', 'space-around', 'inherit'
];
// JS：关键字 + 内置对象/方法名
const JS_KEYWORDS = [
  'let', 'const', 'var', 'function', 'return', 'if', 'else', 'for', 'while',
  'do', 'switch', 'case', 'default', 'break', 'continue', 'new', 'delete',
  'typeof', 'instanceof', 'in', 'of', 'class', 'extends', 'super', 'this',
  'try', 'catch', 'finally', 'throw', 'async', 'await', 'yield', 'import',
  'export', 'from', 'default', 'null', 'undefined', 'true', 'false', 'NaN',
  'console', 'document', 'window', 'Math', 'JSON', 'Object', 'Array', 'String',
  'Number', 'Boolean', 'Map', 'Set', 'Promise', 'Date', 'RegExp', 'Error',
  'localStorage', 'sessionStorage', 'setTimeout', 'setInterval', 'clearTimeout',
  'clearInterval', 'fetch', 'alert', 'parseInt', 'parseFloat', 'isNaN'
];

/** 把「函数名(签名)」批量转成提示项 */
function funcs(list) {
  return list.map(f => ({ label: f.split('(')[0], kind: 'func', detail: f, insert: f.split('(')[0] + '()' }));
}
/** 关键字批量转成提示项 */
function kws(list) {
  return list.map(k => ({ label: k, kind: 'kw', detail: '关键字', insert: k }));
}

export const LANGS = {
  c: {
    name: 'C 语言',
    ext: 'c',
    comment: '//',
    keywords: C_KEYWORDS,
    completions: funcs([
      'printf(const char *format, ...)',
      'scanf(const char *format, ...)',
      'puts(const char *s)',
      'strlen(const char *s)',
      'strcpy(char *dest, const char *src)',
      'strncpy(char *dest, const char *src, size_t n)',
      'strcmp(const char *a, const char *b)',
      'strcat(char *dest, const char *src)',
      'memcpy(void *dest, const void *src, size_t n)',
      'memset(void *s, int c, size_t n)',
      'malloc(size_t size)',
      'calloc(size_t n, size_t size)',
      'realloc(void *ptr, size_t size)',
      'free(void *ptr)',
      'sizeof(type)',
      'fopen(const char *path, const char *mode)',
      'fclose(FILE *fp)',
      'fgets(char *buf, int n, FILE *fp)',
      'fprintf(FILE *fp, const char *fmt, ...)',
      'qsort(void *base, size_t n, size_t size, int (*cmp)(const void*, const void*))',
      'atoi(const char *s)',
      'exit(int status)'
    ]).concat(kws(C_KEYWORDS)).concat([
      { label: 'main', kind: 'snip', detail: '主函数模板', insert: 'int main(void) {\n    \n    return 0;\n}' },
      { label: 'struct', kind: 'snip', detail: '结构体定义', insert: 'struct Name {\n    int field;\n};' },
      { label: 'fori', kind: 'snip', detail: 'for 循环模板', insert: 'for (int i = 0; i < n; i++) {\n    \n}' }
    ])
  },
  cpp: {
    name: 'C++',
    ext: 'cpp',
    comment: '//',
    keywords: CPP_KEYWORDS,
    completions: funcs([
      'std::cout << x << std::endl',
      'std::cin >> x',
      'std::vector<T> v',
      'std::string s',
      'std::map<K, V> m',
      'std::unordered_map<K, V> m',
      'std::sort(begin, end)',
      'std::find(begin, end, value)',
      'std::make_unique<T>(args)',
      'std::make_shared<T>(args)',
      'std::move(x)',
      'std::forward<T>(x)',
      'v.push_back(x)',
      'v.size()',
      'v.begin()',
      'v.end()',
      'std::endl'
    ]).concat(kws(CPP_KEYWORDS)).concat([
      { label: 'class', kind: 'snip', detail: '类定义模板', insert: 'class Name {\npublic:\n    Name() {}\n    ~Name() {}\nprivate:\n    \n};' },
      { label: 'template', kind: 'snip', detail: '函数模板', insert: 'template <typename T>\nT func(T a, T b) {\n    return a + b;\n}' },
      { label: 'forauto', kind: 'snip', detail: '范围 for', insert: 'for (auto &x : container) {\n    \n}' },
      { label: 'maincpp', kind: 'snip', detail: '主函数模板', insert: 'int main() {\n    \n    return 0;\n}' }
    ])
  },
  java: {
    name: 'Java',
    ext: 'java',
    comment: '//',
    keywords: JAVA_KEYWORDS,
    completions: funcs([
      'System.out.println(x)',
      'System.out.printf(fmt, args)',
      'String.format(fmt, args)',
      'str.length()',
      'str.substring(begin, end)',
      'str.split(regex)',
      'str.equals(other)',
      'str.trim()',
      'Arrays.sort(arr)',
      'Arrays.toString(arr)',
      'Collections.sort(list)',
      'list.add(e)',
      'list.get(i)',
      'list.size()',
      'map.put(k, v)',
      'map.get(k)',
      'map.containsKey(k)',
      'Integer.parseInt(s)',
      'Objects.equals(a, b)',
      'Thread.start()',
      'ExecutorService.submit(task)',
      'Optional.ofNullable(x)'
    ]).concat(kws(JAVA_KEYWORDS)).concat([
      { label: 'main', kind: 'snip', detail: '主方法模板', insert: 'public static void main(String[] args) {\n    \n}' },
      { label: 'class', kind: 'snip', detail: '类定义', insert: 'public class Name {\n    \n}' },
      { label: 'foreach', kind: 'snip', detail: '增强 for', insert: 'for (Type item : collection) {\n    \n}' },
      { label: 'trycatch', kind: 'snip', detail: '异常处理', insert: 'try {\n    \n} catch (Exception e) {\n    e.printStackTrace();\n} finally {\n    \n}' }
    ])
  },
  python: {
    name: 'Python',
    ext: 'py',
    comment: '#',
    keywords: PY_KEYWORDS,
    completions: funcs([
      'print(*objects, sep=" ", end="\\n")',
      'len(obj)',
      'range(start, stop, step)',
      'enumerate(iterable, start=0)',
      'zip(*iterables)',
      'map(func, iterable)',
      'filter(func, iterable)',
      'sorted(iterable, key=None, reverse=False)',
      'sum(iterable, start=0)',
      'max(iterable, key=None)',
      'min(iterable, key=None)',
      'abs(x)',
      'round(number, ndigits=None)',
      'isinstance(obj, cls)',
      'list.append(x)',
      'list.extend(iterable)',
      'list.insert(i, x)',
      'list.pop(i=-1)',
      'list.remove(x)',
      'str.split(sep=None)',
      'str.join(iterable)',
      'str.strip(chars=None)',
      'str.format(*args, **kwargs)',
      'dict.get(key, default=None)',
      'dict.items()',
      'dict.keys()',
      'dict.values()',
      'open(file, mode="r", encoding=None)',
      'type(obj)',
      'id(obj)',
      'dir(obj)',
      'set(iterable)'
    ]).concat(kws(PY_KEYWORDS)).concat([
      { label: 'def', kind: 'snip', detail: '函数定义', insert: 'def func(args):\n    """docstring"""\n    return None' },
      { label: 'class', kind: 'snip', detail: '类定义', insert: 'class Name:\n    def __init__(self):\n        pass' },
      { label: 'ifmain', kind: 'snip', detail: '主入口', insert: 'if __name__ == "__main__":\n    main()' },
      { label: 'with', kind: 'snip', detail: '上下文管理器', insert: 'with open(path) as f:\n    data = f.read()' },
      { label: 'try', kind: 'snip', detail: '异常处理', insert: 'try:\n    \nexcept Exception as e:\n    print(e)\nfinally:\n    pass' },
      { label: 'decorator', kind: 'snip', detail: '装饰器', insert: 'def deco(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper' }
    ])
  },

  /* ============ Web 前端三件套 ============ */
  html: {
    name: 'HTML',
    ext: 'html',
    comment: '<!--',
    keywords: HTML_KEYWORDS,
    completions: funcs([
      'document.querySelector(sel)',
      'document.getElementById(id)',
      'element.addEventListener(type, handler)',
      'element.classList.add(cls)',
      'element.textContent',
      'element.innerHTML',
      'element.setAttribute(name, value)'
    ]).concat(kws(HTML_KEYWORDS)).concat([
      { label: 'html5', kind: 'snip', detail: 'HTML5 文档骨架', insert: '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <title>页面标题</title>\n</head>\n<body>\n  \n</body>\n</html>' },
      { label: 'table', kind: 'snip', detail: '表格', insert: '<table>\n  <thead>\n    <tr><th>列名</th></tr>\n  </thead>\n  <tbody>\n    <tr><td>值</td></tr>\n  </tbody>\n</table>' },
      { label: 'form', kind: 'snip', detail: '表单', insert: '<form action="/submit" method="post">\n  <label for="name">姓名</label>\n  <input id="name" name="name" type="text" required>\n  <button type="submit">提交</button>\n</form>' },
      { label: 'ul', kind: 'snip', detail: '无序列表', insert: '<ul>\n  <li>第一项</li>\n  <li>第二项</li>\n</ul>' },
      { label: 'a', kind: 'snip', detail: '超链接', insert: '<a href="https://example.com" target="_blank" rel="noopener">链接文字</a>' },
      { label: 'img', kind: 'snip', detail: '图片', insert: '<img src="photo.png" alt="描述文字" width="200">' }
    ])
  },
  css: {
    name: 'CSS',
    ext: 'css',
    comment: '/*',
    keywords: CSS_KEYWORDS,
    completions: funcs([
      'display: flex',
      'display: grid',
      'justify-content: center',
      'align-items: center',
      'gap: 16px',
      'grid-template-columns: repeat(3, 1fr)',
      'flex-direction: column',
      'position: absolute',
      'transition: all .2s ease',
      'box-sizing: border-box',
      'calc(100% - 32px)',
      'var(--brand)'
    ]).concat(kws(CSS_KEYWORDS)).concat([
      { label: 'center', kind: 'snip', detail: 'flex 居中', insert: 'display: flex;\njustify-content: center;\nalign-items: center;' },
      { label: 'grid3', kind: 'snip', detail: '三列网格', insert: 'display: grid;\ngrid-template-columns: repeat(3, 1fr);\ngap: 16px;' },
      { label: 'card', kind: 'snip', detail: '卡片样式', insert: '.card {\n  background: #fff;\n  border: 1px solid #e5e9f0;\n  border-radius: 12px;\n  padding: 16px;\n  box-shadow: 0 2px 8px rgba(0,0,0,.06);\n}' },
      { label: 'media', kind: 'snip', detail: '响应式断点', insert: '@media (max-width: 768px) {\n  \n}' },
      { label: 'animate', kind: 'snip', detail: '关键帧动画', insert: '@keyframes fadeIn {\n  from { opacity: 0; transform: translateY(8px); }\n  to { opacity: 1; transform: none; }\n}' },
      { label: 'hover', kind: 'snip', detail: '悬浮态', insert: '.btn:hover {\n  transform: translateY(-2px);\n  box-shadow: 0 8px 20px rgba(0,0,0,.12);\n}' }
    ])
  },
  javascript: {
    name: 'JavaScript',
    ext: 'js',
    comment: '//',
    keywords: JS_KEYWORDS,
    completions: funcs([
      'console.log(...data)',
      'document.querySelector(sel)',
      'document.createElement(tag)',
      'Array.from(iterable)',
      'JSON.parse(text)',
      'JSON.stringify(value)',
      'Object.keys(obj)',
      'Object.entries(obj)',
      'setTimeout(fn, delay)',
      'setInterval(fn, delay)',
      'fetch(url, options)',
      'Promise.all(iterable)',
      'localStorage.getItem(key)',
      'localStorage.setItem(key, value)'
    ]).concat(kws(JS_KEYWORDS)).concat([
      { label: 'arrow', kind: 'snip', detail: '箭头函数', insert: 'const fn = (a, b) => {\n  return a + b;\n}' },
      { label: 'forof', kind: 'snip', detail: 'for...of 遍历', insert: 'for (const item of list) {\n  console.log(item);\n}' },
      { label: 'try', kind: 'snip', detail: '异常处理', insert: 'try {\n  \n} catch (err) {\n  console.error(err);\n} finally {\n  \n}' },
      { label: 'fetch', kind: 'snip', detail: 'async 请求', insert: 'async function load() {\n  const res = await fetch("/api/data");\n  const data = await res.json();\n  return data;\n}' },
      { label: 'class', kind: 'snip', detail: '类定义', insert: 'class Name {\n  constructor(value) {\n    this.value = value;\n  }\n}' },
      { label: 'map', kind: 'snip', detail: '数组映射', insert: 'const doubled = list.map(x => x * 2)' },
      { label: 'reduce', kind: 'snip', detail: '数组归约', insert: 'const sum = list.reduce((acc, x) => acc + x, 0)' },
      { label: 'dom', kind: 'snip', detail: 'DOM 事件绑定', insert: 'const btn = document.querySelector("#btn");\nbtn.addEventListener("click", () => {\n  console.log("clicked");\n});' }
    ])
  }
};

/**
 * 内置示例（与 knowledge.route 的 /code/xxx 一一对应）
 * steps: 讲解步骤（配合可视化播放器无法表达时，用「要点列表」呈现）
 */
export const LABS = {
  /* ============ C 语言 ============ */
  'c-pointer': {
    kid: 66,
    lang: 'c', title: '指针与地址运算', points: [
      '指针变量存的是地址：int *p = &a; → p 是 a 的地址，*p 是 a 的值',
      '指针算术按类型步长走：p+1 实际地址 + sizeof(*p)，不是 +1 字节',
      '数组名在多数表达式中退化为首元素指针，但 sizeof(arr) 例外',
      '未初始化/已释放的指针是野指针，解引用属未定义行为'
    ],
    code: `#include <stdio.h>

int main(void) {
    int a = 10;
    int *p = &a;            // p 保存 a 的地址

    printf("a 的值   = %d\\n", a);
    printf("a 的地址 = %p\\n", (void *)&a);
    printf("p 的值   = %p  (等价于 &a)\\n", (void *)p);
    printf("*p 的值  = %d  (等价于 a)\\n", *p);

    *p = 20;                // 通过指针改写 a
    printf("改后 a   = %d\\n", a);

    int arr[3] = {1, 2, 3};
    int *q = arr;           // 数组名退化为首元素指针
    printf("arr[1]   = %d, *(q + 1) = %d\\n", arr[1], *(q + 1));

    printf("指针 +1 实际偏移 = %ld 字节\\n",
           (long)((char *)(q + 1) - (char *)q));   // int 步长 4
    return 0;
}`
  },
  'c-stack': {
    kid: 67,
    lang: 'c', title: '函数调用与栈帧', points: [
      '每次调用在栈上压入一个栈帧：返回地址、形参、局部变量、保存的寄存器',
      '形参是实参的拷贝 → 函数内改形参不影响实参（要改就得传指针）',
      '递归深度过大会栈溢出；返回局部变量地址是经典错误',
      '调用约定决定参数入栈顺序与清栈责任（cdecl/stdcall）'
    ],
    code: `#include <stdio.h>

void swap_by_value(int x, int y) {      // 形参是拷贝
    int t = x; x = y; y = t;
}

void swap_by_pointer(int *x, int *y) {  // 传地址才能真正交换
    int t = *x; *x = *y; *y = t;
}

int fact(int n) {                        // 递归：每层一个栈帧
    if (n <= 1) return 1;
    return n * fact(n - 1);
}

int main(void) {
    int a = 3, b = 5;
    swap_by_value(a, b);
    printf("值传递后: a=%d b=%d  (未改变)\\n", a, b);

    swap_by_pointer(&a, &b);
    printf("地址传递后: a=%d b=%d\\n", a, b);

    printf("5! = %d\\n", fact(5));
    return 0;
}`
  },
  'c-struct': {
    kid: 68,
    lang: 'c', title: '结构体与内存对齐', points: [
      '结构体成员按自身大小对齐，整体大小向最大成员对齐补齐',
      '对齐规则：成员偏移必须是 min(自身大小, 对齐系数) 的整数倍',
      '调换成员顺序可减小内存占用（把大类型放前面）',
      'offsetof / sizeof 用于验证布局；网络传输要防对齐差异'
    ],
    code: `#include <stdio.h>
#include <stddef.h>

struct S1 {          // char + int + char
    char a;          // 偏移 0，补 3 字节
    int  b;          // 偏移 4
    char c;          // 偏移 8，尾部再补 3 → 共 12
};

struct S2 {          // 调换顺序：int 在前
    int  b;          // 偏移 0
    char a;          // 偏移 4
    char c;          // 偏移 5，尾部补 2 → 共 8
};

int main(void) {
    printf("sizeof(struct S1) = %zu\\n", sizeof(struct S1));
    printf("sizeof(struct S2) = %zu\\n", sizeof(struct S2));
    printf("S1: a@%zu b@%zu c@%zu\\n",
           offsetof(struct S1, a), offsetof(struct S1, b), offsetof(struct S1, c));
    printf("S2: b@%zu a@%zu c@%zu\\n",
           offsetof(struct S2, b), offsetof(struct S2, a), offsetof(struct S2, c));

    struct S2 s = {.b = 7, .a = 'A', .c = 'B'};
    printf("s.b=%d s.a=%c s.c=%c\\n", s.b, s.a, s.c);
    return 0;
}`
  },
  'c-array': {
    kid: 69,
    lang: 'c', title: '数组、字符串与越界', points: [
      '数组长度编译期固定（变长数组 VLA 是 C99 可选特性），sizeof 才能拿到元素个数',
      '字符串是以 \\0 结尾的字符数组，strlen 不统计 \\0，sizeof 统计',
      '数组越界写会破坏相邻内存，是缓冲区溢出攻击的根源',
      'char *s = "abc" 是字符串字面量（只读区），char s[] = "abc" 是栈上副本'
    ],
    code: `#include <stdio.h>
#include <string.h>

int main(void) {
    int a[5] = {1, 2, 3, 4, 5};
    printf("元素个数 = %zu\\n", sizeof(a) / sizeof(a[0]));

    char s1[] = "abc";                 // 栈上副本，可修改
    const char *s2 = "abc";            // 只读字面量
    printf("sizeof(s1)=%zu strlen(s1)=%zu\\n", sizeof(s1), strlen(s1));
    printf("sizeof(s2)=%zu strlen(s2)=%zu\\n", sizeof(s2), strlen(s2));

    s1[0] = 'A';
    printf("s1 = %s\\n", s1);
    // s2[0] = 'A';                    // 未定义行为：写入只读区

    // 安全遍历：用长度控制，绝不越界
    for (size_t i = 0; i < sizeof(s1); i++) {
        printf("[%zu]=%d(%c) ", i, s1[i], s1[i] ? s1[i] : '?');
    }
    printf("\\n");
    return 0;
}`
  },
  'c-malloc': {
    kid: 70,
    lang: 'c', title: '动态内存 malloc/free', points: [
      'malloc 在堆上分配未初始化内存，calloc 额外清零',
      '必须检查返回值是否为 NULL；free 后指针置 NULL 防野指针',
      '内存泄漏 = 分配后忘记释放；重复 free / free 栈内存都是未定义行为',
      'malloc 分配的大小自己记账，free 不需要长度参数（分配器内部记录）'
    ],
    code: `#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n = 5;
    int *p = (int *)malloc(n * sizeof(int));   // 堆上分配
    if (p == NULL) {                            // 必须判空
        fprintf(stderr, "分配失败\\n");
        return 1;
    }

    for (int i = 0; i < n; i++) p[i] = i * i;
    for (int i = 0; i < n; i++) printf("%d ", p[i]);
    printf("\\n");

    n = 10;
    int *q = (int *)realloc(p, n * sizeof(int));  // 扩容，可能搬家
    if (q != NULL) p = q;                          // 只有成功才接管
    for (int i = 5; i < n; i++) p[i] = i;
    printf("扩容后: ");
    for (int i = 0; i < n; i++) printf("%d ", p[i]);
    printf("\\n");

    free(p);      // 释放
    p = NULL;     // 置空，避免野指针
    return 0;
}`
  },

  /* ============ C++ ============ */
  'cpp-class': {
    kid: 71,
    lang: 'cpp', title: '类、构造与析构', points: [
      '构造函数负责初始化，析构函数负责清理；二者都不写返回值',
      '初始化列表比在函数体内赋值更高效（直接初始化成员，避免先默认构造再赋值）',
      '成员初始化顺序 = 声明顺序，与初始化列表书写顺序无关（经典坑）',
      '拷贝构造/拷贝赋值/析构三者出现其一，通常三者都要自己写（Rule of Three）'
    ],
    code: `#include <iostream>
#include <string>
using namespace std;

class Student {
    string name_;      // 声明顺序决定初始化顺序
    int age_;
public:
    Student(const string &name, int age) : name_(name), age_(age) {
        cout << "构造: " << name_ << endl;
    }
    Student(const Student &o) : name_(o.name_), age_(o.age_) {
        cout << "拷贝构造" << endl;
    }
    ~Student() { cout << "析构: " << name_ << endl; }

    void introduce() const { cout << name_ << " / " << age_ << endl; }
};

int main() {
    Student a("小明", 20);
    a.introduce();

    Student b = a;      // 调用拷贝构造
    b.introduce();
    return 0;           // 离开作用域，逆序析构 b、a
}`
  },
  'cpp-polymorphism': {
    kid: 72,
    lang: 'cpp', title: '虚函数与运行时多态', points: [
      '基类函数加 virtual，派生类用 override 覆写，通过基类指针/引用调用时动态绑定',
      '对象内有一个虚表指针 vptr，指向类的虚函数表 vtable，运行时查表分派',
      '基类析构函数必须是 virtual，否则通过基类指针 delete 派生对象只会析构基类部分',
      '纯虚函数 (= 0) 构成抽象类，不能实例化；静态绑定发生在编译期，动态绑定在运行时'
    ],
    code: `#include <iostream>
using namespace std;

class Animal {
public:
    virtual void speak() const { cout << "..." << endl; }
    virtual ~Animal() { cout << "~Animal" << endl; }   // 必须是 virtual
};

class Dog : public Animal {
public:
    void speak() const override { cout << "汪汪" << endl; }
    ~Dog() override { cout << "~Dog" << endl; }
};

class Cat : public Animal {
public:
    void speak() const override { cout << "喵喵" << endl; }
    ~Cat() override { cout << "~Cat" << endl; }
};

int main() {
    Animal *p1 = new Dog();
    Animal *p2 = new Cat();
    p1->speak();        // 动态绑定 → 汪汪
    p2->speak();        // 动态绑定 → 喵喵

    delete p1;          // 虚析构 → 先 ~Dog 再 ~Animal
    delete p2;
    return 0;
}`
  },
  'cpp-template': {
    kid: 73,
    lang: 'cpp', title: '模板与泛型编程', points: [
      '函数模板 / 类模板在实例化时生成具体代码，属于编译期多态（零运行时开销）',
      '类型推导：template <typename T>；C++17 起可用 CTAD 省略显式类型',
      '模板定义必须放在头文件（实例化时需要看到完整定义）',
      'typename 用于指明依赖类型；非类型模板参数可传编译期常量'
    ],
    code: `#include <iostream>
#include <vector>
#include <string>
using namespace std;

template <typename T>
T my_max(T a, T b) {                 // 函数模板
    return a > b ? a : b;
}

template <typename T, int N>         // 非类型模板参数
struct Buffer {
    T data[N];
    int size() const { return N; }
};

int main() {
    cout << my_max(3, 7) << endl;              // 推导为 int
    cout << my_max(2.5, 1.5) << endl;          // 推导为 double
    cout << my_max(string("abc"), string("abd")) << endl;

    Buffer<int, 4> buf{};                      // 栈上定长缓冲
    cout << "N = " << buf.size() << endl;

    vector<int> v{1, 2, 3};                    // 类模板实例化
    for (int x : v) cout << x << " ";
    cout << endl;
    return 0;
}`
  },
  'cpp-stl': {
    kid: 74,
    lang: 'cpp', title: 'STL 容器与迭代器', points: [
      '序列容器 vector / deque / list，关联容器 map / set，无序容器 unordered_map / unordered_set',
      'vector 扩容会整体搬家 → 之前的迭代器、引用、指针全部失效',
      'erase 返回下一个有效迭代器：it = v.erase(it)；不要在范围 for 里 erase',
      '选择依据：随机访问用 vector，中间频繁插入删除用 list，查表用 unordered_map'
    ],
    code: `#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
using namespace std;

int main() {
    vector<int> v{5, 2, 8, 1};
    sort(v.begin(), v.end());                     // 算法 + 迭代器
    for (int x : v) cout << x << " ";
    cout << endl;

    auto it = find(v.begin(), v.end(), 8);
    if (it != v.end()) cout << "找到 8，下标 " << (it - v.begin()) << endl;

    map<string, int> score{{"语文", 90}, {"数学", 95}};
    score["英语"] = 88;                            // 下标访问会自动插入
    for (auto &[k, val] : score) cout << k << ":" << val << " ";
    cout << endl;

    // 删除所有偶数：erase 返回下一个有效迭代器
    for (auto i = v.begin(); i != v.end(); ) {
        if (*i % 2 == 0) i = v.erase(i);
        else ++i;
    }
    for (int x : v) cout << x << " ";
    cout << endl;
    return 0;
}`
  },
  'cpp-raii': {
    kid: 75,
    lang: 'cpp', title: '引用、移动语义与 RAII', points: [
      'RAII：资源获取即初始化，把资源生命周期绑定到栈对象，靠析构自动释放',
      'unique_ptr 独占所有权（可 move 不可 copy），shared_ptr 引用计数，weak_ptr 打破循环引用',
      '移动语义把"拷贝"变成"窃取"，std::move 只是把左值强转成右值引用',
      '左值有名字可取地址，右值是临时量；T&& 绑定右值，实现移动构造/移动赋值'
    ],
    code: `#include <iostream>
#include <memory>
#include <vector>
#include <string>
using namespace std;

struct Res {
    string name;
    Res(string n) : name(std::move(n)) { cout << "获取 " << name << endl; }
    ~Res() { cout << "释放 " << name << endl; }   // 离开作用域自动调用
};

int main() {
    {
        unique_ptr<Res> p = make_unique<Res>("文件句柄");
        // unique_ptr<Res> q = p;              // 编译错误：不能拷贝
        unique_ptr<Res> q = std::move(p);      // 可以移动所有权
        cout << "p 是否为空: " << (p == nullptr) << endl;
    }                                          // 自动释放，无需 delete

    shared_ptr<Res> a = make_shared<Res>("共享资源");
    cout << "引用计数 = " << a.use_count() << endl;
    {
        shared_ptr<Res> b = a;
        cout << "引用计数 = " << a.use_count() << endl;
    }
    cout << "引用计数 = " << a.use_count() << endl;

    vector<string> v;
    string s = "很长的字符串内容";
    v.push_back(std::move(s));                 // 移动而非拷贝
    cout << "移动后 s = '" << s << "'" << endl;
    return 0;
}`
  },

  /* ============ Java ============ */
  'java-object': {
    kid: 76,
    lang: 'java', title: '类、对象与 JVM 内存', points: [
      '对象实例在堆，引用变量在栈；new 出来的对象由 GC 回收',
      '== 比较引用地址，equals 比较内容；String 常量池让字面量可复用',
      'Integer 等包装类有缓存（-128~127），超出范围 new 出新对象',
      'static 成员属于类，随类加载而存在，被所有实例共享'
    ],
    code: `public class Main {
    static int counter = 0;                 // 类变量，共享

    String name;                            // 实例变量

    Main(String name) { this.name = name; counter++; }

    public static void main(String[] args) {
        Main a = new Main("A");
        Main b = new Main("B");
        System.out.println("对象个数 = " + Main.counter);

        String s1 = "abc";                  // 常量池
        String s2 = "abc";
        String s3 = new String("abc");      // 堆上新对象
        System.out.println("s1 == s2 : " + (s1 == s2));        // true
        System.out.println("s1 == s3 : " + (s1 == s3));        // false
        System.out.println("s1.equals(s3): " + s1.equals(s3)); // true

        Integer x = 127, y = 127;           // 缓存范围内
        Integer m = 128, n = 128;           // 超出缓存，各自 new
        System.out.println("x == y : " + (x == y));            // true
        System.out.println("m == n : " + (m == n));            // false
    }
}`
  },
  'java-collection': {
    kid: 77,
    lang: 'java', title: '集合框架 Collection', points: [
      'List 有序可重复（ArrayList 数组 / LinkedList 链表），Set 无序去重，Map 键值对',
      'ArrayList 查询 O(1)、中间插入 O(n)；LinkedList 插入 O(1)、查询 O(n)',
      'HashMap 数组+链表/红黑树，初始容量 16，负载因子 0.75，扩容翻倍',
      '遍历时结构性修改会抛 ConcurrentModificationException，要用 Iterator.remove'
    ],
    code: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>();
        list.add("Java");
        list.add("Python");
        list.add("Java");                      // List 允许重复
        System.out.println("List = " + list);

        Set<String> set = new HashSet<>(list); // 去重 + 无序
        System.out.println("Set  = " + set);

        Map<String, Integer> map = new HashMap<>();
        map.put("语文", 90);
        map.put("数学", 95);
        map.put("语文", 92);                   // 覆盖旧值
        System.out.println("语文 = " + map.get("语文"));
        for (Map.Entry<String, Integer> e : map.entrySet()) {
            System.out.println(e.getKey() + " -> " + e.getValue());
        }

        // 安全删除：用迭代器，不要 foreach 里 remove
        Iterator<String> it = list.iterator();
        while (it.hasNext()) {
            if (it.next().equals("Java")) it.remove();
        }
        System.out.println("删除后 = " + list);
    }
}`
  },
  'java-exception': {
    kid: 78,
    lang: 'java', title: '异常机制', points: [
      'Throwable → Error（JVM 级，不可恢复）/ Exception（可处理）',
      'Exception 分受检异常（编译期强制处理，如 IOException）与运行时异常（RuntimeException）',
      'try-catch-finally：finally 一定执行（除非 JVM 退出或 System.exit）',
      'try-with-resources 自动关闭实现 AutoCloseable 的资源，替代 finally'
    ],
    code: `import java.io.*;

public class Main {
    static int divide(int a, int b) {
        if (b == 0) throw new ArithmeticException("除数不能为 0");
        return a / b;
    }

    public static void main(String[] args) {
        try {
            System.out.println(divide(10, 2));
            System.out.println(divide(10, 0));      // 抛出运行时异常
        } catch (ArithmeticException e) {
            System.out.println("捕获: " + e.getMessage());
        } finally {
            System.out.println("finally 总会执行");
        }

        // try-with-resources：自动关闭，无需 finally
        try (BufferedReader br = new BufferedReader(new StringReader("第一行\\n第二行"))) {
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println("读到: " + line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}`
  },
  'java-thread': {
    kid: 79,
    lang: 'java', title: '多线程与并发', points: [
      '创建线程：继承 Thread 或实现 Runnable/Callable，推荐线程池',
      'synchronized 保证互斥 + 可见性；volatile 只保证可见性与禁止重排，不保证原子性',
      '线程状态：NEW → RUNNABLE → BLOCKED/WAITING/TIMED_WAITING → TERMINATED',
      'wait/notify 必须在 synchronized 块内调用；并发容器优先用 ConcurrentHashMap'
    ],
    code: `import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    static int unsafe = 0;                        // 无保护
    static AtomicInteger safe = new AtomicInteger(0);

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        CountDownLatch latch = new CountDownLatch(1000);

        for (int i = 0; i < 1000; i++) {
            pool.submit(() -> {
                unsafe++;                         // 非原子：可能丢失更新
                safe.incrementAndGet();           // 原子类：线程安全
                latch.countDown();
            });
        }
        latch.await();
        pool.shutdown();

        System.out.println("unsafe = " + unsafe + "  (可能 < 1000)");
        System.out.println("safe   = " + safe.get() + "  (一定 = 1000)");

        // synchronized 互斥
        Object lock = new Object();
        synchronized (lock) {
            System.out.println("临界区，同一时刻只有一个线程");
        }
    }
}`
  },
  'java-generic': {
    kid: 80,
    lang: 'java', title: '泛型与反射', points: [
      '泛型是编译期语法糖，运行时类型擦除（T → Object 或上界）',
      '<?> 无界通配（只读）、<? extends T> 上界（生产者）、<? super T> 下界（消费者）→ PECS 原则',
      '不能 new T()、不能 new T[]、不能用 instanceof 判断具体泛型类型',
      '反射可在运行时获取 Class 信息、创建对象、调用方法，但破坏封装且有性能开销'
    ],
    code: `import java.lang.reflect.*;
import java.util.*;

public class Main {
    static <T> void printList(List<T> list) {       // 泛型方法
        for (T t : list) System.out.print(t + " ");
        System.out.println();
    }
    static double sum(List<? extends Number> nums) { // 上界通配：只读
        double s = 0;
        for (Number n : nums) s += n.doubleValue();
        return s;
    }

    public static void main(String[] args) throws Exception {
        List<Integer> ints = Arrays.asList(1, 2, 3);
        printList(ints);
        System.out.println("sum = " + sum(ints));

        // 类型擦除验证
        System.out.println("运行时类型相同: " +
            (new ArrayList<Integer>().getClass() == new ArrayList<String>().getClass()));

        // 反射：运行时拿到类信息并调用方法
        Class<?> clazz = Class.forName("java.util.ArrayList");
        Object obj = clazz.getDeclaredConstructor().newInstance();
        Method add = clazz.getMethod("add", Object.class);
        add.invoke(obj, "反射加入的元素");
        Method size = clazz.getMethod("size");
        System.out.println("通过反射调用后 size = " + size.invoke(obj));
    }
}`
  },

  /* ============ Python ============ */
  'py-list': {
    kid: 81,
    lang: 'python', title: '列表、切片与推导式', points: [
      '切片 lst[a:b:c] 是浅拷贝（新列表对象），修改切片不影响原列表的第一层',
      'lst[start:stop] 含头不含尾；负数索引从末尾算；步长为 -1 可反转',
      '列表推导式 [expr for x in it if cond] 比 append 循环更快更简洁',
      '可变对象作为默认参数会被所有调用共享（经典坑，用 None 代替）'
    ],
    code: `# 切片：含头不含尾，步长可负
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print("nums[2:5]  =", nums[2:5])      # [2, 3, 4]
print("nums[:3]   =", nums[:3])       # [0, 1, 2]
print("nums[-3:]  =", nums[-3:])      # [7, 8, 9]
print("nums[::-1] =", nums[::-1])     # 反转
print("nums[::2]  =", nums[::2])      # 隔一个取

# 切片是浅拷贝
a = [1, 2, 3]
b = a[:]
b[0] = 99
print("a =", a, " b =", b)           # a 不受影响

# 列表推导式
squares = [x * x for x in range(10) if x % 2 == 0]
print("偶数平方 =", squares)

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
col = [row[1] for row in matrix]      # 取第 1 列
print("第 1 列 =", col)

# 可变默认参数的坑
def append_to(x, target=None):
    if target is None:
        target = []
    target.append(x)
    return target

print(append_to(1), append_to(2))     # [1] [2]，不会累积`
  },
  'py-decorator': {
    kid: 82,
    lang: 'python', title: '函数、参数与装饰器', points: [
      '参数顺序：位置参数 → 默认参数 → *args → 关键字参数 → **kwargs',
      '装饰器本质是高阶函数：@deco 等价于 func = deco(func)',
      '用 functools.wraps 保留原函数的 __name__ 与文档',
      '带参装饰器 = 三层嵌套：deco(arg) 返回真正的装饰器'
    ],
    code: `import time
import functools

def timer(func):                              # 装饰器：统计耗时
    @functools.wraps(func)                    # 保留元信息
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        cost = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} 耗时 {cost:.3f} ms")
        return result
    return wrapper

def repeat(n):                                # 带参装饰器：三层嵌套
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return deco

@timer
def slow_add(a, b):
    time.sleep(0.01)
    return a + b

@repeat(3)
def greet(name):
    print(f"你好, {name}")

print("结果 =", slow_add(3, 4))
greet("小明")

# 参数解包
def show(a, b, *args, **kwargs):
    print(f"a={a} b={b} args={args} kwargs={kwargs}")

show(1, 2, 3, 4, x=10, y=20)
show(*[1, 2], **{"x": 100})`
  },
  'py-class': {
    kid: 83,
    lang: 'python', title: '面向对象与魔术方法', points: [
      '__init__ 初始化、__str__ 面向用户、__repr__ 面向调试',
      '实例属性在 __init__ 里定义；类属性被所有实例共享，可变类属性会被"串改"',
      '@property 把方法变成属性访问，可加 setter 做校验',
      '__slots__ 限制属性、节省内存；继承用 super()，MRO 决定查找顺序'
    ],
    code: `class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):                 # 运算符重载
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __str__(self):                        # print 时调用
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):                       # 调试/容器显示
        return f"Vector({self.x!r}, {self.y!r})"

v1, v2 = Vector(1, 2), Vector(3, 4)
print("v1 + v2 =", v1 + v2)
print("v1 == Vector(1, 2) :", v1 == Vector(1, 2))
print([v1, v2])                               # 用 repr


class Student:
    school = "某大学"                          # 类属性，共享

    def __init__(self, name, score):
        self.name = name
        self._score = score

    @property
    def score(self):                          # 只读属性
        return self._score

    @score.setter
    def score(self, value):                   # 带校验的写入
        if not 0 <= value <= 100:
            raise ValueError("分数必须在 0~100")
        self._score = value

    def __str__(self):
        return f"{self.school} - {self.name}: {self._score}"

s = Student("小红", 88)
s.score = 95                                  # 走 setter
print(s)
# s.score = 150                               # 抛 ValueError`
  },
  'py-generator': {
    kid: 84,
    lang: 'python', title: '迭代器与生成器', points: [
      '可迭代对象实现 __iter__，迭代器实现 __iter__ + __next__',
      '生成器函数用 yield：调用返回生成器，惰性求值、节省内存',
      '生成器只能遍历一次；想重复用就转成列表或重新调用',
      '生成器表达式 (x for x in ...) 比列表推导式更省内存'
    ],
    code: `# 生成器函数：遇到 yield 暂停，保留现场
def fib(n):
    a, b = 0, 1
    count = 0
    while count < n:
        yield a                     # 产出并暂停
        a, b = b, a + b
        count += 1

print("前 10 个斐波那契:", list(fib(10)))

# 惰性：不会一次性占用全部内存
gen = (x * x for x in range(10 ** 6))
print("生成器表达式类型:", type(gen).__name__)
print("取前 5 个:", [next(gen) for _ in range(5)])

# 手动驱动迭代器
it = iter([10, 20, 30])
print(next(it), next(it), next(it))
# print(next(it))                   # StopIteration

# 自定义可迭代对象
class CountDown:
    def __init__(self, start): self.start = start
    def __iter__(self):
        n = self.start
        while n > 0:
            yield n
            n -= 1

print("倒计时:", list(CountDown(5)))

# 生成器只能消费一次
g = fib(5)
print("第一次:", list(g), "第二次:", list(g))`
  },
  'py-exception': {
    kid: 85,
    lang: 'python', title: '异常与上下文管理器', points: [
      'try / except / else / finally：else 在无异常时执行，finally 一定执行',
      'except 按子类在前、父类在后的顺序书写；用 as e 获取异常对象',
      'raise ... from e 保留异常链；自定义异常继承 Exception',
      'with 语句调用 __enter__/__exit__，保证资源一定被释放'
    ],
    code: `class ScoreError(ValueError):                 # 自定义异常
    pass

def check(score):
    if not isinstance(score, int):
        raise TypeError("分数必须是整数")
    if not 0 <= score <= 100:
        raise ScoreError(f"分数越界: {score}")
    return score

for s in [88, 150, "abc"]:
    try:
        print("合法:", check(s))
    except ScoreError as e:                    # 子类在前
        print("业务异常:", e)
    except (TypeError, ValueError) as e:       # 父类型兜底
        print("类型/值异常:", e)
    else:
        print("无异常，走 else")
    finally:
        print("-- 本轮结束 --")

# 上下文管理器：自动关闭资源
class Timer:
    def __enter__(self):
        import time; self.t = time.perf_counter(); return self
    def __exit__(self, exc_type, exc, tb):
        import time
        print(f"耗时 {time.perf_counter() - self.t:.4f}s")
        return False                           # False = 不吞掉异常

with Timer():
    sum(range(10 ** 6))

# 异常链
try:
    check(150)
except ScoreError as e:
    raise RuntimeError("校验流程失败") from e`
  },

  /* ============ HTML ============ */
  'html-structure': {
    kid: 86,
    lang: 'html', title: 'HTML5 文档骨架与语义化', points: [
      '<!DOCTYPE html> 声明标准模式；<html lang="zh-CN"> 声明语言，影响朗读与断词',
      '<head> 放元信息（charset / viewport / title），<body> 放可见内容',
      '语义化标签（header/nav/main/article/aside/footer）让结构与含义同时被表达',
      'meta viewport 是移动端不缩放的开关：width=device-width, initial-scale=1',
      '一个页面只应有一个 <h1>，标题层级按 h1→h2→h3 不跳级'
    ],
    code: `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>语义化页面结构</title>
</head>
<body>
  <header>
    <h1>CSVisual 学习笔记</h1>
    <nav>
      <a href="#ds">数据结构</a>
      <a href="#net">计算机网络</a>
    </nav>
  </header>

  <main>
    <article id="ds">
      <h2>什么是栈</h2>
      <p>栈是<b>后进先出</b>的线性表，只允许在栈顶插入和删除。</p>
      <ul>
        <li>入栈 push</li>
        <li>出栈 pop</li>
      </ul>
    </article>
  </main>

  <footer>
    <p>&copy; 2026 CSVisual</p>
  </footer>
</body>
</html>`
  },
  'html-form': {
    kid: 87,
    lang: 'html', title: '表单与输入校验', points: [
      '<form> 的 action 决定提交地址，method 决定 GET / POST',
      '<label for="id"> 与控件的 id 关联，点击文字也能聚焦控件（无障碍必需）',
      'HTML5 内置校验：required / pattern / min / max / type="email"',
      'name 属性是提交时的字段名；没有 name 的控件不会被提交',
      'type="submit" 触发表单提交，type="button" 只是普通按钮'
    ],
    code: `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>用户注册表单</title>
</head>
<body>
  <h1>注册账号</h1>

  <form action="/api/register" method="post">
    <p>
      <label for="username">用户名</label>
      <input id="username" name="username" type="text"
             required minlength="3" maxlength="16" placeholder="3-16 个字符">
    </p>

    <p>
      <label for="email">邮箱</label>
      <!-- type=email 会让浏览器自动校验格式 -->
      <input id="email" name="email" type="email" required>
    </p>

    <p>
      <label for="age">年龄</label>
      <input id="age" name="age" type="number" min="1" max="120">
    </p>

    <p>
      <label for="role">身份</label>
      <select id="role" name="role">
        <option value="student">学生</option>
        <option value="teacher">教师</option>
      </select>
    </p>

    <p>
      <label for="agree">
        <input id="agree" name="agree" type="checkbox" required> 我已阅读用户协议
      </label>
    </p>

    <button type="submit">提交注册</button>
    <button type="button">仅重置</button>
  </form>
</body>
</html>`
  },
  'html-table-list': {
    kid: 88,
    lang: 'html', title: '表格与列表', points: [
      '表格用于「数据」而非布局：thead/tbody/tfoot 分区，th 表头，td 单元格',
      'colspan / rowspan 合并列与行，注意合并后后续行要少写对应的单元格',
      '<ul> 无序、<ol> 有序、<dl> 定义列表（dt 术语 + dd 解释）',
      '表格必须写 caption 或前置标题，否则读屏软件无法理解其含义',
      '嵌套列表要把子列表放在 <li> 内部，而不是放成兄弟节点'
    ],
    code: `<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>表格与列表</title></head>
<body>
  <h1>各算法时间复杂度对比</h1>

  <table border="1">
    <caption>常见排序算法复杂度</caption>
    <thead>
      <tr>
        <th>算法</th>
        <th>最好</th>
        <th>平均</th>
        <th>最坏</th>
        <th>稳定性</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>冒泡排序</td><td>O(n)</td><td>O(n²)</td><td>O(n²)</td><td>稳定</td></tr>
      <tr><td>快速排序</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n²)</td><td>不稳定</td></tr>
      <tr><td>归并排序</td><td>O(n log n)</td><td>O(n log n)</td><td>O(n log n)</td><td>稳定</td></tr>
      <tr>
        <!-- colspan 合并两列作为总结行 -->
        <td colspan="4">以上都在原地或 O(n) 辅助空间内完成</td>
        <td>—</td>
      </tr>
    </tbody>
  </table>

  <h2>学习路线</h2>
  <ol>
    <li>基础语法
      <ul>
        <li>变量与类型</li>
        <li>流程控制</li>
      </ul>
    </li>
    <li>数据结构</li>
    <li>算法设计</li>
  </ol>
</body>
</html>`
  },
  'html-media': {
    kid: 89,
    lang: 'html', title: '超链接、图片与多媒体', points: [
      'href 可以是绝对 URL、相对路径或页内锚点 #id',
      'target="_blank" 必须配 rel="noopener"：否则新页面能通过 window.opener 反向操作本页',
      '<img> 的 alt 是图片加载失败时的替代文本，也是无障碍的关键',
      '<img> 用 width/height 预设尺寸可避免加载时布局跳动（CLS）',
      '<figure>/<figcaption> 给图表配标题，语义比 div+p 更准确'
    ],
    code: `<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>链接与图片</title></head>
<body>
  <h1>链接、图片与语义容器</h1>

  <!-- 页内锚点：点击跳到 id=part2 的位置 -->
  <p><a href="#part2">跳到第二部分</a></p>

  <!-- 外链必须带 rel=noopener -->
  <p>
    <a href="https://developer.mozilla.org" target="_blank" rel="noopener">
      MDN Web 文档（新窗口打开）
    </a>
  </p>

  <h2 id="part2">第二部分</h2>

  <!-- alt 是必要的：图片挂了或读屏时靠它传达信息 -->
  <figure>
    <img src="stack.png" alt="栈的入栈出栈示意图" width="320" height="180">
    <figcaption>图 1 栈的后进先出特性</figcaption>
  </figure>

  <video controls width="360" poster="cover.jpg">
    <source src="demo.mp4" type="video/mp4">
    你的浏览器不支持 video 标签，请
    <a href="demo.mp4">下载视频</a>后观看。
  </video>
</body>
</html>`
  },
  'html-a11y': {
    kid: 90,
    lang: 'html', title: '无障碍与文档元信息', points: [
      'aria-label 给没有可见文本的控件补名称（如图标按钮）',
      'role 显式声明元素角色；能用的原生标签优先，别滥用 role',
      'tabindex="0" 让自定义控件可被 Tab 聚焦；正值会打乱 Tab 顺序，一般不推荐',
      'lang 属性影响读屏发音；中英混排时局部加 lang="en"',
      'SEO 相关：title、meta description、语义化标题层级'
    ],
    code: `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="CSVisual：计算机专业多学科可视化智能学习平台">
  <title>无障碍友好的页面</title>
</head>
<body>
  <h1>无障碍要点演示</h1>

  <!-- 图标按钮没有可见文字，必须用 aria-label 说明用途 -->
  <button aria-label="关闭对话框">
    <span aria-hidden="true">✕</span>
  </button>

  <!-- 装饰性图标对读屏隐藏，避免念出无意义内容 -->
  <p>
    <span aria-hidden="true">★</span>
    收藏本页
  </p>

  <!-- 表单错误提示与控件关联 -->
  <label for="pwd">密码</label>
  <input id="pwd" type="password" aria-describedby="pwd-tip" required>
  <small id="pwd-tip">至少 8 位，需包含字母和数字</small>

  <!-- 中英混排时标注英文，读屏发音才正确 -->
  <p>学习 <span lang="en">Stack</span> 这种数据结构</p>

  <!-- 状态变化用 aria-live 通知读屏 -->
  <div role="status" aria-live="polite">已保存</div>
</body>
</html>`
  },

  /* ============ CSS ============ */
  'css-box': {
    kid: 91,
    lang: 'css', title: '盒模型与 box-sizing', points: [
      '盒模型从内到外：content → padding → border → margin',
      '默认 content-box：width 只含内容，加 padding/border 后总宽变大',
      'border-box：width 含 padding 和 border，布局计算直观得多',
      '垂直方向相邻 margin 会合并（取较大值），水平方向不会',
      'margin 可以是负值把元素拉近；padding 不能为负'
    ],
    code: `/* 全局改成 border-box 是现代项目的通行做法：
   写 width: 300px 就真的是 300px，不再被 padding 撑大 */
*, *::before, *::after {
  box-sizing: border-box;
}

.box-content {
  box-sizing: content-box;   /* 演示对比用 */
  width: 200px;
  padding: 20px;
  border: 5px solid #3b6ef6;
  /* 实际占宽 = 200 + 20*2 + 5*2 = 250px */
}

.box-border {
  box-sizing: border-box;
  width: 200px;
  padding: 20px;
  border: 5px solid #22a06b;
  /* 实际占宽就是 200px，内容区被压缩为 150px */
}

/* 垂直 margin 合并：两者间距是 24px 而不是 16+24=40px */
.m-merge-a { margin-bottom: 16px; }
.m-merge-b { margin-top: 24px; }

/* 居中：margin auto 只对水平方向有效 */
.center-h {
  width: 60%;
  margin: 0 auto;
}`
  },
  'css-selector': {
    kid: 92,
    lang: 'css', title: '选择器与优先级', points: [
      '优先级权重：行内样式(1000) > id(100) > class/属性/伪类(10) > 标签/伪元素(1)',
      '!important 会压过一切行内样式之外的选择器，能不用就不用',
      '后代选择器 A B 带空格；直接子元素 A > B；相邻兄弟 A + B',
      '伪类 :hover/:focus/:nth-child(2n)；伪元素 ::before/::after 需配 content',
      '同权重时后写的生效（层叠）；继承来的样式永远优先于直接命中的样式'
    ],
    code: `/* 权重依次递增，最后一行的 color 生效 */
p { color: #333; }                       /* (0,0,1) */
.note { color: #3b6ef6; }                /* (0,1,0) */
#intro { color: #e8a13a; }               /* (1,0,0) */
#intro.note { color: #22a06b; }          /* (1,1,0) 生效 */

/* 直接子元素：只选 .list 下第一层的 li */
.list > li {
  padding: 6px 10px;
  border-bottom: 1px solid #eef1f6;
}

/* 相邻兄弟：紧跟在 h2 后面的 p */
h2 + p { margin-top: 4px; font-size: 14px; }

/* 结构化伪类：斑马纹 */
.list li:nth-child(2n) { background: #f8fafc; }

/* 伪元素必须写 content */
.tip::before {
  content: "💡 ";
}

/* 属性选择器 */
input[type="email"] { border-color: #3b6ef6; }
a[href^="https"]::after { content: " ↗"; }

/* 状态伪类：可交互元素必须有可见的焦点态（无障碍要求） */
.btn:hover { background: #5a86ff; }
.btn:focus-visible { outline: 2px solid #3b6ef6; outline-offset: 2px; }`
  },
  'css-flex': {
    kid: 93,
    lang: 'css', title: 'Flexbox 弹性布局', points: [
      'display:flex 后主轴默认为水平，flex-direction 可改为 column',
      'justify-content 管主轴对齐，align-items 管交叉轴对齐',
      'flex: 1 展开是 flex-grow:1 flex-shrink:1 flex-basis:0%',
      'flex-grow 分配「剩余空间」，flex-basis 决定分空间前的初始宽度',
      'min-width:0 是 flex 子项能被压缩的开关，不加就压不下去（文字溢出常见坑）'
    ],
    code: `/* 1. 水平居中 + 垂直居中 */
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

/* 2. 导航栏：两端对齐，中间均匀分布 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #eef1f6;
}
.navbar .brand { font-weight: 700; }
.navbar .links { display: flex; gap: 18px; }

/* 3. 三栏自适应：两侧固定宽度，中间吃满剩余空间 */
.layout { display: flex; gap: 16px; }
.layout .side { flex: 0 0 220px; }      /* 不伸不缩，固定 220px */
.layout .main { flex: 1 1 auto; min-width: 0; }  /* min-width:0 才压得住 */

/* 4. 卡片等高：flex 默认 stretch，子项自动拉平 */
.cards { display: flex; align-items: stretch; gap: 12px; }
.card { flex: 1; display: flex; flex-direction: column; }
.card .body { flex: 1; }               /* 把底部按钮推到底 */
.card .foot { margin-top: auto; }

/* 5. 换行：不等宽内容自动折行 */
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tags span { padding: 3px 10px; border-radius: 12px; background: #eef3ff; }`
  },
  'css-grid': {
    kid: 94,
    lang: 'css', title: 'Grid 网格布局', points: [
      'fr 是剩余空间的份数单位；repeat(3, 1fr) 等价于 1fr 1fr 1fr',
      'grid-template-areas 用命名区域描述版式，可读性最好',
      'gap 同时控制行列间距，比旧式 margin 方案干净',
      'auto-fit + minmax 是最省事的响应式写法，不用写媒体查询',
      'Grid 管二维、Flex 管一维；不要用 Grid 做单行排列'
    ],
    code: `/* 1. 三列等宽网格（最常用） */
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* 2. 响应式：每列最小 220px，能放几列放几列。
   auto-fit 会把多余空轨道收起，auto-fill 则保留 —— 卡片布局用 fit */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

/* 3. 命名区域：头部 / 侧栏 / 主内容 / 页脚 */
.page {
  display: grid;
  grid-template-columns: 220px 1fr;
  grid-template-rows: 60px 1fr 48px;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  gap: 12px;
  min-height: 100vh;
}
.page > header { grid-area: header; }
.page > aside  { grid-area: sidebar; }
.page > main   { grid-area: main; min-width: 0; }
.page > footer { grid-area: footer; }

/* 4. 跨行跨列 */
.dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.dashboard .span-2 { grid-column: span 2; }   /* 横跨两列 */
.dashboard .span-2-rows { grid-row: span 2; } /* 纵跨两行 */

/* 5. 固定列 + 自适应列混排 */
.form-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 10px;
  align-items: center;
}`
  },
  'css-responsive': {
    kid: 95,
    lang: 'css', title: '响应式与媒体查询', points: [
      '移动优先：先写小屏样式，再用 min-width 断点增强',
      'viewport meta 是响应式的前提，缺了它移动端会按桌面宽度缩放',
      'min-width / max-width 断点方向相反，混用会造成样式互相覆盖难排查',
      '相对单位：rem 随根字号缩放，vw/vh 随视口，% 随父元素',
      'clamp(min, 理想值, max) 可以在一行内实现字号平滑缩放'
    ],
    code: `/* 移动优先：默认样式面向小屏，断点向上增强 */
.card-list {
  display: grid;
  grid-template-columns: 1fr;   /* 手机：单列 */
  gap: 12px;
  padding: 12px;
}

/* 平板及以上：两列 */
@media (min-width: 640px) {
  .card-list { grid-template-columns: repeat(2, 1fr); gap: 16px; padding: 16px; }
}

/* 桌面及以上：三列 */
@media (min-width: 1024px) {
  .card-list { grid-template-columns: repeat(3, 1fr); padding: 24px; }
}

/* 超宽屏：限制内容宽度，避免长行难读 */
@media (min-width: 1600px) {
  .card-list { max-width: 1440px; margin: 0 auto; }
}

/* 流体字号：视口 320px 时 16px，1280px 时 24px，中间平滑过渡 */
h1 {
  font-size: clamp(16px, 2vw + 12px, 24px);
}

/* 用 rem 让整体随根字号缩放（用户放大字号时布局跟着走） */
body { font-size: 1rem; line-height: 1.7; }
.sub { font-size: 0.875rem; }

/* 尊重系统的「减少动态效果」偏好 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}`
  },

  /* ============ JavaScript ============ */
  'js-basics': {
    kid: 96,
    lang: 'javascript', title: '变量、类型与相等判断', points: [
      'let 可重新赋值、const 不可（但对象内部属性仍可改）、var 有变量提升已被淘汰',
      'JS 只有 7 种原始类型 + object；typeof null === "object" 是历史遗留 bug',
      '== 会做隐式类型转换（"1" == 1 为 true），一律用 === 严格相等',
      'NaN 不等于任何值包括自身，判断用 Number.isNaN()',
      '假值只有 6 个：false / 0 / "" / null / undefined / NaN'
    ],
    code: `// ---- 声明方式 ----
let count = 0;          // 可重新赋值
const PI = 3.14159;     // 不可重新赋值
const user = { name: "Tom" };
user.name = "Jerry";    // 对象内容仍可改（const 锁的是绑定，不是内容）

// ---- 原始类型 ----
console.log(typeof "abc");        // string
console.log(typeof 42);           // number
console.log(typeof true);         // boolean
console.log(typeof undefined);    // undefined
console.log(typeof null);         // object  ← 历史遗留 bug
console.log(typeof Symbol());     // symbol
console.log(typeof 123n);         // bigint

// ---- 相等判断 ----
console.log(1 == "1");            // true  ← 隐式转换，应避免
console.log(1 === "1");           // false ← 用这个
console.log(null == undefined);   // true
console.log(null === undefined);  // false

// NaN 的坑
console.log(NaN === NaN);              // false
console.log(Number.isNaN(NaN));        // true  ← 正确判断方式

// ---- 六种假值 ----
const falsy = [false, 0, "", null, undefined, NaN];
console.log(falsy.filter(v => !v).length);   // 6，全部是假值
console.log([] ? "真" : "假");               // 真 —— 空数组是对象，为真

// ---- 模板字符串 ----
const name = "CSVisual";
console.log(\`欢迎使用 \${name}，共 \${2 + 3} 门核心课\`);`
  },
  'js-array': {
    kid: 97,
    lang: 'javascript', title: '数组与高阶函数', points: [
      'map 一对一转换，filter 筛选，reduce 归约 —— 都不改原数组（返回新数组）',
      'sort 会原地修改数组，且默认按字符串排序，数字排序必须传比较函数',
      'some 任一满足即真，every 全部满足才真，find 返回首个匹配元素',
      'slice 不改原数组，splice 会改；展开运算符 ... 是浅拷贝',
      '稀疏与越界访问返回 undefined，不会报错'
    ],
    code: `const students = [
  { name: "小明", score: 92, city: "北京" },
  { name: "小红", score: 78, city: "上海" },
  { name: "小刚", score: 85, city: "北京" },
];

// map：一对一转换
const names = students.map(s => s.name);
console.log("姓名:", names);

// filter：筛选（不改原数组）
const passed = students.filter(s => s.score >= 85);
console.log("85 分以上:", passed.map(s => s.name));

// reduce：归约成单个值
const total = students.reduce((sum, s) => sum + s.score, 0);
console.log("总分:", total, "平均:", (total / students.length).toFixed(1));

// find / some / every
console.log("第一个北京学生:", students.find(s => s.city === "北京")?.name);
console.log("有不及格的吗:", students.some(s => s.score < 60));
console.log("都及格了吗:", students.every(s => s.score >= 60));

// ---- sort 的坑：默认按字符串比较 ----
const nums = [10, 9, 100, 1];
console.log("默认排序:", [...nums].sort());            // [1, 10, 100, 9] 错的
console.log("数值排序:", [...nums].sort((a, b) => a - b));  // [1, 9, 10, 100]

// 按分数降序（sort 原地修改，先复制一份）
const ranked = [...students].sort((a, b) => b.score - a.score);
console.log("排名:", ranked.map(s => \`\${s.name}(\${s.score})\`).join(" > "));

// slice vs splice
console.log("slice(0,2):", names.slice(0, 2));  // 不改原数组
const copy = [...names];
copy.splice(0, 1, "新同学");                     // 会改 copy
console.log("splice 后:", copy);`
  },
  'js-object': {
    kid: 98,
    lang: 'javascript', title: '对象、解构与展开', points: [
      '解构可取值、可设默认值、可重命名：const { a, b = 1, c: alias } = obj',
      '展开运算符 ... 是浅拷贝：嵌套对象仍是同一个引用',
      'Object.entries / keys / values 是遍历对象的常用组合',
      '可选链 ?. 在中间为 null/undefined 时短路，比逐层判断安全',
      '空值合并 ?? 只在 null/undefined 时取默认值，与 || 不同（0 和 "" 不算空）'
    ],
    code: `const user = {
  name: "小明",
  age: 20,
  address: { city: "北京", district: "海淀" },
  tags: ["前端", "算法"],
};

// ---- 解构 ----
const { name, age } = user;
const { city } = user.address;
const { name: userName, gender = "未知" } = user;   // 重命名 + 默认值
console.log(name, age, city, userName, gender);

// ---- 展开运算符：浅拷贝 ----
const copy = { ...user, age: 21 };        // age 被覆盖，其余复制
console.log("原对象未被改动:", user.age, "新对象:", copy.age);

// 浅拷贝的陷阱：嵌套对象仍是同一引用
const shallow = { ...user };
shallow.address.city = "上海";
console.log("原对象也被改了:", user.address.city);   // 上海 ← 共享引用

// 深拷贝（结构化克隆，现代浏览器原生支持）
const deep = structuredClone(user);
deep.address.city = "广州";
console.log("这次原对象没变:", user.address.city);

// ---- 遍历 ----
console.log("keys:", Object.keys(user));
console.log("values:", Object.values(user).length);
for (const [k, v] of Object.entries(user)) {
  console.log(\`  \${k} = \${typeof v === "object" ? "[object]" : v}\`);
}

// ---- 可选链与空值合并 ----
console.log(user.address?.city);          // 北京
console.log(user.contact?.phone);         // undefined，不报错
console.log(user.contact?.phone ?? "未填写");   // 未填写

// ?? 与 || 的区别：0 和 "" 在 ?? 眼里是有效值
console.log(0 || "默认");    // 默认
console.log(0 ?? "默认");    // 0   ← 更符合直觉`
  },
  'js-dom': {
    kid: 99,
    lang: 'javascript', title: 'DOM 操作与事件', points: [
      'querySelector 返回首个匹配，querySelectorAll 返回静态 NodeList',
      '事件绑定用 addEventListener，可以绑多个且便于解绑',
      '事件冒泡：子元素事件会向上传播，用 stopPropagation 阻止',
      '事件委托：把监听器挂在父元素上，处理动态生成的子元素',
      'innerHTML 会重新解析 HTML 有 XSS 风险；纯文本用 textContent'
    ],
    code: `// ---- 查询 ----
const list = document.querySelector("#list");
const items = document.querySelectorAll(".item");   // 静态列表
console.log("项数:", items.length);

// ---- 创建与插入 ----
function addItem(text) {
  const li = document.createElement("li");
  li.className = "item";
  li.dataset.id = String(Date.now());   // 写入 data-id 属性
  li.textContent = text;                // 纯文本，安全
  list.appendChild(li);
  return li;
}
addItem("新任务");

// ---- 改样式与类 ----
const first = list.querySelector(".item");
first.classList.add("done");
first.classList.toggle("highlight");
first.style.color = "#3b6ef6";

// ---- 事件委托：给动态子元素也能响应 ----
list.addEventListener("click", (e) => {
  const li = e.target.closest(".item");
  if (!li) return;                       // 点到了空白处
  li.classList.toggle("done");
  console.log("点击了:", li.textContent, "data-id =", li.dataset.id);
});

// ---- 表单与输入 ----
const input = document.querySelector("#task-input");
input?.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;         // 只在回车时提交
  const value = e.target.value.trim();
  if (!value) return;
  addItem(value);
  e.target.value = "";
});

// ---- 阻止默认行为 ----
document.querySelector("form")?.addEventListener("submit", (e) => {
  e.preventDefault();                    // 不让浏览器真的提交刷新页面
  console.log("改为用 fetch 提交");
});

// ---- 安全提醒：避免 XSS ----
// element.innerHTML = userInput;        // 危险：能注入 <script>
element.textContent = userInput;         // 安全：当纯文本`

  },
  'js-async': {
    kid: 100,
    lang: 'javascript', title: '异步、Promise 与事件循环', points: [
      'JS 单线程：同步代码先执行完，宏任务/微任务随后按队列执行',
      '微任务（Promise.then）优先于宏任务（setTimeout）执行',
      'await 会暂停当前 async 函数，但不阻塞主线程',
      'Promise.all 全部成功才成功；allSettled 无论成败都返回结果',
      'await 循环里要小心串行执行导致的性能问题，能并发就 Promise.all'
    ],
    code: `// ---- 执行顺序：这是面试与调试都绕不开的一点 ----
console.log("1 同步");

setTimeout(() => console.log("4 宏任务 setTimeout"), 0);

Promise.resolve().then(() => console.log("3 微任务 then"));

console.log("2 同步结束");
// 输出顺序：1 同步 → 2 同步结束 → 3 微任务 → 4 宏任务
// 原因：同步 > 微任务 > 宏任务

// ---- async / await ----
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function run() {
  console.log("开始");
  await delay(100);              // 暂停这个函数，不阻塞主线程
  console.log("100ms 后继续");
}
run();

// ---- 错误处理：try/catch 捕获 await 的 reject ----
async function safeLoad() {
  try {
    const res = await fetch("/api/data");
    if (!res.ok) throw new Error("HTTP " + res.status);
    return await res.json();
  } catch (err) {
    console.error("加载失败:", err.message);
    return null;
  }
}

// ---- 并发 vs 串行 ----
// 串行：总耗时 = 各任务之和
async function serial(ids) {
  const out = [];
  for (const id of ids) out.push(await fetch("/api/item/" + id));
  return out;
}
// 并发：总耗时 = 最慢那个
async function parallel(ids) {
  const out = await Promise.all(ids.map(id => fetch("/api/item/" + id)));
  return out;
}

// ---- Promise.all vs allSettled ----
const results = await Promise.allSettled([
  Promise.resolve("ok"),
  Promise.reject(new Error("failed")),
]);
console.log(results);
// [{status:"fulfilled", value:"ok"}, {status:"rejected", reason:Error}]
`
  }
};

/* ============================================================
   CSS 实验室的「被作用对象」
   为什么单独放一张表：CSS 没有配套的 HTML 就看不见效果，
   而编辑器一次只能编辑一份代码。这里为每个 CSS 实验室准备一段示例标记，
   预览时拼成 <style>{用户代码}</style> + {示例标记}，改样式立刻能看到变化。
   ============================================================ */
export const LAB_DEMOS = {
  'css-box': `<div class="box-content">content-box：width 200 + padding 40 + border 10 = 250px</div>
<div class="box-border">border-box：总宽就是 200px，内容区被压缩</div>

<div class="m-merge-a">A：margin-bottom 16px</div>
<div class="m-merge-b">B：margin-top 24px（垂直 margin 合并，间距取 24 而非 40）</div>

<div class="center-h">水平居中：margin: 0 auto</div>`,

  'css-selector': `<p id="intro" class="note">这句话同时被 4 条规则命中，看谁最终生效</p>

<ul class="list">
  <li>第 1 项（:nth-child(2n) 斑马纹）</li>
  <li>第 2 项</li>
  <li>第 3 项
    <ul>
      <li>嵌套项：.list &gt; li 选不到我（不是直接子元素）</li>
    </ul>
  </li>
  <li>第 4 项</li>
</ul>

<h2>标题</h2>
<p>紧跟在 h2 后面的段落（h2 + p 命中）</p>
<p class="tip">带 ::before 伪元素的提示</p>

<input type="email" placeholder="邮箱（属性选择器命中）">
<input type="text" placeholder="普通文本框">

<a href="https://example.com">外部链接（::after 会加 ↗）</a>

<button class="btn">点我或按 Tab 聚焦看焦点态</button>`,

  'css-flex': `<div class="center">水平 + 垂直都居中</div>

<nav class="navbar">
  <span class="brand">CSVisual</span>
  <span class="links">
    <a href="#">课程</a><a href="#">题库</a><a href="#">算法</a>
  </span>
</nav>

<div class="layout">
  <aside class="side">侧栏固定 220px</aside>
  <main class="main">主内容 flex:1，min-width:0 才压得住长单词 supercalifragilisticexpialidocious</main>
</div>

<div class="cards">
  <div class="card"><div class="body">卡片一<br>内容少</div><div class="foot">底部按钮</div></div>
  <div class="card"><div class="body">卡片二<br>内容<br>比较多<br>但底部仍对齐</div><div class="foot">底部按钮</div></div>
  <div class="card"><div class="body">卡片三</div><div class="foot">底部按钮</div></div>
</div>

<div class="tags">
  <span>Flexbox</span><span>Grid</span><span>响应式</span><span>盒模型</span>
  <span>选择器</span><span>动画</span><span>无障碍</span>
</div>`,

  'css-grid': `<div class="grid-3">
  <div class="box">1</div><div class="box">2</div><div class="box">3</div>
</div>

<div class="auto-grid">
  <div class="box">自动</div><div class="box">适应</div><div class="box">列数</div><div class="box">第 4 个</div>
</div>

<div class="page">
  <header>header（grid-area: header）</header>
  <aside>sidebar</aside>
  <main>main 内容区</main>
  <footer>footer</footer>
</div>

<div class="dashboard">
  <div class="box span-2">跨两列</div>
  <div class="box">普通</div>
  <div class="box span-2-rows">跨两行</div>
  <div class="box">普通</div>
  <div class="box">普通</div>
</div>

<div class="form-row">
  <label>用户名</label>
  <input placeholder="100px + 1fr 两列">
</div>`,

  'css-responsive': `<h1>流体字号标题（拖动窗口宽度观察列数变化）</h1>
<p class="sub">移动优先：默认单列，≥640px 两列，≥1024px 三列</p>

<div class="card-list">
  <div class="box">卡片 1</div>
  <div class="box">卡片 2</div>
  <div class="box">卡片 3</div>
  <div class="box">卡片 4</div>
  <div class="box">卡片 5</div>
  <div class="box">卡片 6</div>
</div>`
};

/** 按 route 的最后一段取示例 */
export function getLabByRoute(route) {
  if (!route) return null;
  const slug = String(route).replace(/^\/?code\//, '');
  return LABS[slug] || null;
}

/** 取实验室配套的示例标记（CSS 预览用） */
export function getLabDemo(slug) {
  return LAB_DEMOS[slug] || '';
}

export default { LANGS, LABS, LAB_DEMOS, getLabByRoute, getLabDemo };
