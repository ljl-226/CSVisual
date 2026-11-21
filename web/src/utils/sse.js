/**
 * SSE 流式请求工具。
 *
 * 为什么不用原生 EventSource：它只支持 GET，也无法带 Authorization 头，
 * 而我们的对话接口要 POST 一整段题面 / 代码。所以这里用 fetch + ReadableStream 自己解 SSE 帧。
 *
 * 用法：
 *   const ctrl = streamPost('/api/agent/chat/stream', payload, {
 *     onMeta(obj)  {},   // 推理过程、推荐动作等元信息，正文之前到达
 *     onDelta(str) {},   // 增量文本
 *     onReplace(obj){},  // 输出校验拦截：整段替换为安全话术（content 覆盖正文）
 *     onDone(obj)  {},   // 结束，obj.mode 标识大模型 / 本地降级
 *     onError(err) {}    // 失败（含 HTTP 错误码）
 *   })
 *   ctrl.abort()        // 用户主动停止
 */
export function streamPost(path, body, handlers = {}) {
  const { onMeta, onDelta, onReplace, onDone, onError, onAbort } = handlers || {}
  const token = readToken()
  const ctrl = new AbortController()
  // 兜底超时：DeepSeek 思考模式下开放 120s，这里再多给一点，防止连接永久挂住
  const timer = setTimeout(() => ctrl.abort(), 180000)
  let got = false

  const fail = err => {
    clearTimeout(timer)
    onError && onError(err)
  }

  ;(async () => {
    try {
      const resp = await fetch(path, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
          ...(token ? { Authorization: 'Bearer ' + token } : {})
        },
        body: JSON.stringify(body || {}),
        signal: ctrl.signal
      })

      if (!resp.ok) {
        let msg = '服务返回 ' + resp.status
        try {
          const j = await resp.json()
          if (j && j.message) msg = j.message
        } catch (e) { /* 非 JSON 就用默认文案 */ }
        return fail(new Error(msg))
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buf = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        let idx
        while ((idx = buf.indexOf('\n\n')) >= 0) {
          handleFrame(buf.slice(0, idx))
          buf = buf.slice(idx + 2)
        }
      }
      if (buf.trim()) handleFrame(buf)

      clearTimeout(timer)
      // 一个字节的正文都没收到就断了 = 这次流是空的，交给上层降级
      if (!got) return fail(new Error('EMPTY_STREAM'))
      onDone && onDone({})
    } catch (e) {
      clearTimeout(timer)
      if (e && e.name === 'AbortError') {
        onAbort && onAbort()
        return
      }
      fail(e)
    }
  })()

  function handleFrame(frame) {
    let data = ''
    for (const line of String(frame).split('\n')) {
      if (line.startsWith(':')) continue // 心跳注释行
      if (line.startsWith('data:')) data += line.slice(5).trim()
    }
    if (!data) return
    let payload
    try { payload = JSON.parse(data) } catch (e) { return }
    got = true
    if (payload.type === 'meta') onMeta && onMeta(payload)
    // delta 的正文字段名：Node 侧叫 content，Python 侧叫 text。
    // 两套后端共用同一个数据库、也共用同一个前端，字段名不一致 = 走 Python 后端时
    // 每一帧正文都拿到空串，界面上就是「思考过程有、回答是空气泡」。
    // 这里两边都认，并且明确判空：宁可不给内容也别把 undefined 喂给打字机。
    else if (payload.type === 'delta') onDelta && onDelta(deltaText(payload))
    else if (payload.type === 'replace') onReplace && onReplace(payload)
    else if (payload.type === 'done') onDone && onDone(payload)
    else if (payload.type === 'error') fail(new Error(payload.message || '流式响应失败'))
  }

  return {
    abort() {
      clearTimeout(timer)
      try { ctrl.abort() } catch (e) { /* 已结束 */ }
    }
  }
}

/** 兼容两套后端的 delta 字段命名，空值一律归一成空串 */
function deltaText(payload) {
  const v = payload && (payload.content !== undefined ? payload.content : payload.text)
  return v === undefined || v === null ? '' : String(v)
}

function readToken() {
  try {
    // 与 Pinia store 读的是同一个 key，保证流式请求和 axios 请求用同一份 token
    return localStorage.getItem('cv_token') || ''
  } catch (e) {
    return ''
  }
}

/**
 * 打字机缓冲：流式文本常常是一阵一阵地到（网络攒包），
 * 直接渲染会"一段一段糊上来"。这里排队后按固定节奏吐字符，观感才是逐字输出。
 *
 * @param {() => string} read  读当前已渲染文本
 * @param {(v: string) => void} write 写回渲染（调用方负责触发滚动）
 */
export function useTypewriter(read, write) {
  let buffer = ''
  let timer = null
  let finished = false

  // 积压越多吐得越快：短答案慢条斯理，长答案不至于让用户等半天
  const step = () => {
    if (buffer.length <= 24) return 1
    return Math.min(14, Math.ceil(buffer.length / 22))
  }

  function tick() {
    if (!buffer.length) {
      if (finished) { timer = null; return }
      timer = setTimeout(tick, 18)
      return
    }
    const n = step()
    const piece = buffer.slice(0, n)
    buffer = buffer.slice(n)
    write(String(read() || '') + piece)
    timer = setTimeout(tick, 18)
  }

  return {
    push(text) {
      const t = String(text || '')
      if (!t) return
      buffer += t
      if (!timer) timer = setTimeout(tick, 18)
    },
    /** 服务端已结束：把剩余 buffer 尽快排干净 */
    finish() {
      finished = true
      if (!timer) timer = setTimeout(tick, 18)
    },
    stop() {
      if (timer) clearTimeout(timer)
      timer = null
      buffer = ''
      finished = true
    }
  }
}
