/* ================= 各语言的空白骨架模板 =================
 * 需求：切到某种语言时，如果这个语言没有现成的等价实现（variant），
 * 至少要给学生一份能直接跑起来的骨架，而不是一片空白或者残留上一个语言的代码。
 *
 * 骨架按在线评测的实际约定写，不是随便缩进一下的伪代码：
 *   - C  : main  返回 int，用 printf 输出
 *   - C++: 关闭 cin/cout 同步，竞赛里 IO 快很多
 *   - Java: 类名必须固定 Main（评测机按这个约定找入口），读 stdin 用 Scanner
 *   - Py  : sys.stdin 整块读入，跨行输入也不会漏
 *   - JS  : Node 环境下 readFileSync(0) 读 stdin，配 vm 才能跑（见 webSandbox）
 *
 * 注释里一律写「请在此输入您的代码」，和实验室里其他示例的措辞保持一致。 */

/* ================= 全站语言顺序（唯一数据源） =================
 * 需求：项目里所有语言列表都用同一个顺序 —— C、C++、Java、Python、JavaScript。
 *
 * 之前每处各写一份，顺序就乱了：AlgorithmDetail.vue 是
 * python, c, cpp, java, javascript（Python 排第一，因为库里原本只有 Python 答案），
 * 而 codeLabs.js 是 c, cpp, java, python, javascript。用户在不同页面看到
 * 同一个下拉却是不同顺序，会以为是两套东西。
 *
 * 放在这里而不是各自文件里，是因为这个顺序和「各语言骨架」是同一件事：
 * 语言的身份（键、显示名、顺序、默认骨架）本就该有一个定义处。
 * 别的文件要顺序就 import LANG_ORDER，别再自己写死一份。
 *
 * 前端语言（html / css）排在最后且用不同色标 —— 它们不是「编译语言」，
 * 点运行走的是浏览器沙箱，和前面五个不是一回事。 */
export const LANG_ORDER = ['c', 'cpp', 'java', 'python', 'javascript', 'html', 'css']

/** 显示名。key 与 LANG_ORDER 一致；没登记的语言原样返回 key（不吞掉） */
export const LANG_LABELS = {
  c: 'C',
  cpp: 'C++',
  java: 'Java',
  python: 'Python',
  javascript: 'JavaScript',
  html: 'HTML',
  css: 'CSS'
}

/** 按 LANG_ORDER 排一组语言 id。传进来的未知 id 排在末尾，不丢 */
export function sortLangs(langs) {
  const uniq = Array.from(new Set(langs || []))
  return uniq.sort((a, b) => {
    const ia = LANG_ORDER.indexOf(a)
    const ib = LANG_ORDER.indexOf(b)
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib)
  })
}

/** 某语言的显示名 */
export function langLabel(lang) {
  return LANG_LABELS[lang] || lang || ''
}

/* 空白骨架。内容与用户给的五段模板逐字一致（只把注释行缩进对齐到代码块，
   这不影响运行，也比顶格更易读）。
   不要在这里加任何「示例代码」—— 新手进来看到的第一行应该是能直接改的框架，
   不是看不懂的完整程序。 */
export const BASE_TEMPLATES = {
  c: `#include <stdio.h>
#include <stdlib.h>
int main(int argc, char *argv[])
{
    // 请在此输入您的代码
    return 0;
}
`,
  cpp: `#include <iostream>
using namespace std;
int main()
{
    // 请在此输入您的代码
    return 0;
}
`,
  java: `import java.util.Scanner;
// 1: 无需 package
// 2: 类名必须 Main，不可修改
public class Main {
    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        // 请在此输入您的代码
        scan.close();
    }
}
`,
  python: `import os
import sys
# 请在此输入您的代码
`,
  javascript: `function main() {
    // 请在此输入您的代码
}

main()
`
}

/** 取某语言的骨架；html/css 没有「编译」概念，不给骨架 */
export function baseTemplate(lang) {
  return BASE_TEMPLATES[lang] || ''
}

/**
 * 切语言时该显示什么代码。三级回退，从具体到通用：
 *   1. 这个语言下用户自己写过的（草稿 / 内存缓存）—— 优先级最高，绝不能覆盖
 *   2. 该语言在本实验里的等价实现（labVariants 的 VARIANTS）
 *   3. 该语言的基础骨架
 * 都拿不到才返回空串（此时应提示「该语言暂无可用模板」）。
 */
export function pickCode(lang, saved, variantCode) {
  if (saved && saved.trim()) return saved
  if (variantCode && variantCode.trim()) return variantCode
  return baseTemplate(lang)
}
