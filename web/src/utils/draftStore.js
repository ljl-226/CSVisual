/* ================= 编辑器草稿：本地持久化 =================
 * 需求：内置编译器与文本编辑器都要有记忆功能 —— 刷新页面、关掉浏览器再回来，
 * 上次写到一半的代码还在。
 *
 * 为什么按「页面 + 标识 + 语言」三级分键：
 *   - 不加语言段 → 切语言就把上一语言的代码当成新语言的草稿（上一轮踩过这个坑）
 *   - 不加标识段 → A 实验的草稿会串到 B 实验
 *   - 不加页面段 → 代码实验室和算法题都是 `cv_draft_xxx`，同名互相覆盖
 *
 * 键名保持短：localStorage 是同步 API，键名越长越占配额；
 * 同时限制单条草稿长度，超长直接不存（十几 MB 的代码存进去会拖慢每一次读写）。
 */
const PREFIX = 'cv_draft_'
/** 单条草稿上限 200KB。localStorage 通常只有 5MB，一条超长代码就能把它撑爆。 */
const MAX_LEN = 200 * 1024

/** 页面标识：同一页面的不同实例要共用草稿 */
export const SCOPE = {
  LAB: 'lab',        // 代码实验室
  ALGO: 'algo',      // 算法题详情
  PRACTICE: 'prac'   // 随堂练习的编程题
}

function key(scope, ident, lang) {
  return PREFIX + scope + '_' + ident + '_' + (lang || 'x')
}

export function loadDraft(scope, ident, lang) {
  if (!ident) return ''
  try {
    return localStorage.getItem(key(scope, ident, lang)) || ''
  } catch (e) {
    // 隐私模式下 localStorage 直接抛异常（不是返回 null），必须 try 包住
    return ''
  }
}

/** 空内容视为「没有草稿」，顺手把旧键清掉，避免还残留一份空串占位 */
export function saveDraft(scope, ident, lang, text) {
  if (!ident) return
  try {
    const k = key(scope, ident, lang)
    if (text && text.trim()) {
      if (text.length > MAX_LEN) {
        localStorage.removeItem(k)
        return
      }
      localStorage.setItem(k, text)
    } else {
      localStorage.removeItem(k)
    }
  } catch (e) { /* 配额不足 / 隐私模式：静默忽略，不影响写代码 */ }
}

/* ================= 运行输入（stdin）草稿 =================
 * 和代码草稿分开存，但同样按「页面 + 标识 + 语言」三级分键：
 * scanf 的测试数据和 Java 的输入样例本来就不是一回事，混着存会互相覆盖；
 * 输入通常很短，不设 200KB 那条限制也能存，但键名仍然控制在可接受长度。
 */
const STDIN_PREFIX = 'cv_stdin_'

function stdinKey(scope, ident, lang) {
  return STDIN_PREFIX + scope + '_' + ident + '_' + (lang || 'x')
}

export function loadStdin(scope, ident, lang) {
  if (!ident) return ''
  try {
    return localStorage.getItem(stdinKey(scope, ident, lang)) || ''
  } catch (e) {
    return ''
  }
}

export function saveStdin(scope, ident, lang, text) {
  if (!ident) return
  try {
    const k = stdinKey(scope, ident, lang)
    if (text && text.trim()) localStorage.setItem(k, text)
    else localStorage.removeItem(k)
  } catch (e) { /* 配额不足 / 隐私模式：忽略 */ }
}

export function clearDraft(scope, ident, lang) {
  try { localStorage.removeItem(key(scope, ident, lang)) } catch (e) { /* 忽略 */ }
}

/** 一次存多语言（代码实验室切语言前用得上：把整份 codeByLang 落盘） */
export function saveDraftMap(scope, ident, map) {
  if (!ident || !map) return
  Object.keys(map).forEach(lang => saveDraft(scope, ident, lang, map[lang]))
}

export function loadDraftMap(scope, ident, langs) {
  const out = {}
  ;(langs || []).forEach(lang => {
    const v = loadDraft(scope, ident, lang)
    if (v) out[lang] = v
  })
  return out
}
