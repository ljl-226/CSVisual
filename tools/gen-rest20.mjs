/**
 * 题库补齐生成器：把「每节 20 题」的缺口一次性补齐
 * ------------------------------------------------------------
 * 背景：seed-core20.sql 只覆盖了课程 1-4（数据结构/计网/操作系统/组成原理）的
 * 43 个知识点，课程 5-18 的知识点还停留在 3~9 题。本脚本依据
 * tools/qdata-rest/manifest.json（由数据库实时算出的缺口）生成补题 SQL，
 * 让全部 117 个知识点都达到 20 题。
 *
 * 与 gen-core20.mjs 的差异：
 *   1. 数量不是写死的 20，而是 manifest 里每个知识点的 need（= 20 - 现有题量）；
 *   2. 多一道「与题干重复」校验，避免和库里已有的 1140 道题撞车；
 *   3. 数据目录独立（qdata-rest），不会被 gen-core20 的 *.js 全量扫描捞走。
 *
 * 用法：node tools/gen-rest20.mjs                    生成 SQL + 打印汇总
 *      node tools/gen-rest20.mjs --check             只校验不写文件
 *      node tools/gen-rest20.mjs --only=rest-c.js    只处理指定文件（逗号分隔，便于分批编写）
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const DATA_DIR = path.join(ROOT, 'tools', 'qdata-rest')
const OUT = path.join(ROOT, 'server-py', 'sql', 'seed-rest20.sql')
const CHECK_ONLY = process.argv.includes('--check')
const onlyArg = (process.argv.find((a) => a.startsWith('--only=')) || '').slice(7)
const ONLY = onlyArg ? onlyArg.split(',').filter(Boolean) : null

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

// 判断题的落地形态必须和管理端写入的形态一致：
// 答案是 A/B，且带上固定的「A=正确 / B=错误」两个选项。
// 曾经这里按 T/F 写答案且 options 留空，结果前端 Practice 页拿不到任何选项，
// 294 道判断题直接变成「没有可点的选项」，学生一道都答不了。
// 数据写成 T 还是 A 后端判分都能认，但 UI 只能渲染 options。
const JUDGE_OPTIONS = '[{"key":"A","text":"正确"},{"key":"B","text":"错误"}]'
const judgeAnswer = (a) => (String(a).toUpperCase() === 'T' ? 'A' : 'B')

const manifest = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'manifest.json'), 'utf8'))
const existing = new Set(JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'existing-titles.json'), 'utf8')))

// ---- 汇总：文件 -> 知识点 -> 题 ----
const files = Object.keys(manifest).sort().filter((f) => !ONLY || ONLY.includes(f))
const all = []
for (const f of files) {
  const p = path.join(DATA_DIR, f)
  if (!fs.existsSync(p)) {
    console.error('[缺少数据文件] ' + p)
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
const err = (msg) => { console.error('  ✗ ' + msg); errors++ }
const seenTitle = new Set()
const perKid = new Map()
const allowed = new Map()

for (const file of files) {
  for (const it of manifest[file]) allowed.set(it.kid, it)
}
const needOf = new Map()
for (const file of files) {
  for (const it of manifest[file]) needOf.set(it.kid, it.need)
}

for (const { file, list } of all) {
  const kidsInFile = new Set(manifest[file].map((x) => x.kid))
  list.forEach((it, idx) => {
    const tag = file + '#' + idx
    if (!it.k) return err(tag + ' 缺少 knowledge_id')
    if (!allowed.has(it.k)) return err(tag + ' knowledge_id ' + it.k + ' 不在 manifest 中')
    if (!kidsInFile.has(it.k)) return err(tag + ' knowledge_id ' + it.k + ' 不属于本文件 ' + file)
    if (!it.q) return err(tag + ' 缺少题干')
    if (existing.has(it.q)) return err(tag + ' 题干与库中已有题目重复: ' + it.q.slice(0, 30) + '...')
    if (seenTitle.has(it.q)) return err(tag + ' 题干在本批内重复')
    seenTitle.add(it.q)
    if (!it.e) return err(tag + ' 缺少解析')
    if (String(it.e).length < 15) return err(tag + ' 解析过短（<15 字），敷衍解析不如不写')

    if (it.t === 's' || it.t === 'm') {
      if (!Array.isArray(it.o) || it.o.length < 2) return err(tag + ' 选择题缺少选项')
      if (new Set(it.o).size !== it.o.length) return err(tag + ' 选项内容重复')
      if (!it.a) return err(tag + ' 缺少答案')
      else {
        const keys = it.o.map((_, i) => ['A', 'B', 'C', 'D', 'E'][i])
        if (it.t === 'm' && String(it.a).length < 2) return err(tag + ' 多选题答案应含 2 个及以上字母')
        for (const ch of String(it.a)) {
          if (!keys.includes(ch)) return err(tag + ' 答案 ' + it.a + ' 超出选项范围')
        }
      }
    } else if (it.t === 'j') {
      if (it.a !== 'T' && it.a !== 'F') return err(tag + ' 判断题答案必须是 T/F')
      if (it.o) return err(tag + ' 判断题不应带选项')
    } else {
      return err(tag + ' 未知题型 ' + it.t)
    }
    perKid.set(it.k, (perKid.get(it.k) || 0) + 1)
  })
}

// 数量必须精确等于缺口（--only 时只校验本批涉及的知识点）
for (const [kid, need] of needOf) {
  if (ONLY && !files.some((f) => manifest[f].some((x) => x.kid === kid))) continue
  const got = perKid.get(kid) || 0
  if (got !== need) err('kid ' + kid + '（' + allowed.get(kid).kname + '）应补 ' + need + ' 题，实得 ' + got + ' 题')
}

const total = all.reduce((n, x) => n + x.list.length, 0)
if (errors) {
  console.error('\n校验未通过，共 ' + errors + ' 处问题，未生成 SQL')
  process.exit(1)
}
console.log('校验通过：' + files.length + ' 个文件 / ' + perKid.size + ' 个知识点 / ' + total + ' 道题')
if (CHECK_ONLY || ONLY) {
  console.log(ONLY ? '（--only 模式：不写 SQL，全部文件就绪后再整体生成）' : '（--check 模式：未写文件）')
  process.exit(0)
}

// ---- 生成 SQL ----
const chunks = []
chunks.push('-- ============================================================')
chunks.push('--  习题补齐：课程 5-18 全部知识点补足到每节 20 题')
chunks.push('--  共 ' + total + ' 道题，覆盖 ' + perKid.size + ' 个知识点')
chunks.push('--  本文件由 tools/gen-rest20.mjs 依据 tools/qdata-rest/*.js 生成，请勿手工编辑')
chunks.push('--  执行顺序：... -> seed-core20 -> seed-algo200 -> seed-rest20')
chunks.push('-- ============================================================')
chunks.push('')

for (const { file, list } of all) {
  chunks.push('-- ---------- ' + file + ' ----------')
  chunks.push('INSERT INTO question (knowledge_id, type, title, options, answer, analysis, score) VALUES')
  const rows = list.map((it) => {
    const type = it.t === 's' ? 'single' : it.t === 'm' ? 'multi' : 'judge'
    const options = it.t === 'j' ? JUDGE_OPTIONS : optJson(it.o)
    const answer = it.t === 'j' ? judgeAnswer(it.a) : it.a
    const score = it.t === 'm' ? 8 : 5
    return "(" + it.k + ",'" + type + "','" + esc(it.q) + "',\n '" + esc(options) + "',\n '"
      + esc(answer) + "','" + esc(it.e) + "'," + score + ")"
  })
  chunks.push(rows.join(',\n') + ';')
  chunks.push('')
}

fs.writeFileSync(OUT, chunks.join('\n'), 'utf8')
console.log('已生成 ' + path.relative(ROOT, OUT).replace(/\\/g, '/'))
