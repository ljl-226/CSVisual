/**
 * 临时工具：把 tools/qdata/*.js 里编写的题目数据生成为 server-py/sql/seed-core20.sql
 * 之所以不手写 SQL：题干里天然含有大量单引号（如 A' 、O(n') ，手写极易写出非法转义，
 * 由脚本统一做 MySQL 字符串转义可以彻底避免这类语法错误。
 *
 * 用法：node tools/gen-core20.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const DATA_DIR = path.join(ROOT, 'tools', 'qdata')
const OUT = path.join(ROOT, 'server-py', 'sql', 'seed-core20.sql')

/** MySQL 单引号字符串转义：先转义反斜杠，再转义单引号 */
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
}

function optJson(list) {
  const keys = ['A', 'B', 'C', 'D', 'E']
  return JSON.stringify((list || []).map((text, i) => ({ key: keys[i], text })))
}

const FILES = fs.readdirSync(DATA_DIR)
  .filter((f) => f.endsWith('.js'))
  .sort()

const NAMES = { ds: '数据结构与算法', net: '计算机网络', os: '操作系统', co: '计算机组成原理' }
function labelOf(f) {
  const m = /^core-([a-z]+)/.exec(f)
  return (m ? NAMES[m[1]] || m[1] : f) + '（' + f + '）'
}

const all = []
for (const f of FILES) {
  const p = path.join(DATA_DIR, f)
  if (!fs.existsSync(p)) {
    console.error('缺少数据文件: ' + p)
    process.exit(1)
  }
  const mod = await import('file://' + p.replace(/\\/g, '/'))
  const list = mod.default || mod
  if (!Array.isArray(list)) {
    console.error(f + ' 必须导出数组')
    process.exit(1)
  }
  all.push({ file: f, list })
}

// ---- 校验 ----
let errors = 0
const perKid = new Map()
for (const { file, list } of all) {
  list.forEach((it, idx) => {
    const tag = file + '#' + idx
    if (!it.k) { console.error(tag + ' 缺少 knowledge_id'); errors++; }
    if (!it.q) { console.error(tag + ' 缺少题干'); errors++; }
    if (!it.e) { console.error(tag + ' 缺少解析'); errors++; }
    if (it.t === 's' || it.t === 'm') {
      if (!Array.isArray(it.o) || it.o.length < 2) { console.error(tag + ' 选择题缺少选项'); errors++; }
      if (!it.a) { console.error(tag + ' 缺少答案'); errors++; }
      else {
        const keys = it.o.map((_, i) => ['A', 'B', 'C', 'D', 'E'][i])
        for (const ch of String(it.a)) {
          if (!keys.includes(ch)) { console.error(tag + ' 答案 ' + it.a + ' 超出选项范围'); errors++; }
        }
      }
    } else if (it.t === 'j') {
      if (it.a !== 'T' && it.a !== 'F') { console.error(tag + ' 判断题答案必须是 T/F'); errors++; }
    } else {
      console.error(tag + ' 未知题型 ' + it.t); errors++;
    }
    perKid.set(it.k, (perKid.get(it.k) || 0) + 1)
  })
}
if (errors) {
  console.error('校验未通过，共 ' + errors + ' 处问题')
  process.exit(1)
}

// ---- 生成 SQL ----
const chunks = []
chunks.push('-- ============================================================')
chunks.push('--  核心课程习题扩充：每节 20 题')
chunks.push('--  课程 1-4（数据结构与算法 / 计算机网络 / 操作系统 / 计算机组成原理）')
chunks.push('--  共 ' + all.reduce((n, x) => n + x.list.length, 0) + ' 道题，'
  + perKid.size + ' 个知识点')
chunks.push('--  本文件由 tools/gen-core20.mjs 依据 tools/qdata/*.js 生成，请勿手工编辑')
chunks.push('--  执行顺序：... -> seed-web -> seed-textbook -> seed-core20')
chunks.push('-- ============================================================')
chunks.push('')

for (const { file, list } of all) {
  chunks.push('-- ---------- ' + labelOf(file) + ' ----------')
  chunks.push('INSERT INTO question (knowledge_id, type, title, options, answer, analysis, score) VALUES')
  const rows = list.map((it) => {
    const type = it.t === 's' ? 'single' : it.t === 'm' ? 'multi' : 'judge'
    const options = (it.t === 'j') ? '[]' : optJson(it.o)
    const score = it.t === 'm' ? 8 : 5
    return "(" + it.k + ",'" + type + "','" + esc(it.q) + "',\n '" + esc(options) + "',\n '"
      + esc(it.a) + "','" + esc(it.e) + "'," + score + ")"
  })
  chunks.push(rows.join(',\n') + ';')
  chunks.push('')
}

fs.writeFileSync(OUT, chunks.join('\n'), 'utf8')

// ---- 汇总 ----
console.log('已生成 ' + path.relative(ROOT, OUT))
console.log('题目总数: ' + all.reduce((n, x) => n + x.list.length, 0))
const kids = [...perKid.keys()].sort((a, b) => a - b)
console.log('知识点数: ' + kids.length)
console.log('每知识点新增: ' + kids.map((k) => 'k' + k + '=' + perKid.get(k)).join(' '))
