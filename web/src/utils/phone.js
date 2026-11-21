/**
 * 联系电话合法性校验（中国大陆手机号）。
 *
 * 只用在「申请临时密码」这一处，但这一处必须卡严：管理员是照着这个号码打电话
 * 核实身份的，填成 123456 或座机，申请就等于白提一次。
 *
 * 放行常见书写形式（+86 / 0086 / 空格 / 连字符 / 括号），
 * 但「通过即归一」——存库和展示都用 11 位裸号，管理员复制到拨号盘就能直接拨。
 * 后端把同一套规则实现在 auth 路由里，前端只是第一道拦。
 */

/** 允许出现的字符：数字与常见分隔书写符号。字母中文一律挡掉，免得「abc138…」蒙混过关 */
const ALLOWED_CHARS = /^[\d+\-()\s]{6,20}$/

/** 号段规则：1 开头 + 第二位 3-9（工信部已放开的民用号段）+ 共 11 位 */
const CN_MOBILE = /^1[3-9]\d{9}$/

export function normalizePhone(raw) {
  let digits = String(raw || '').replace(/\D/g, '')
  // 去掉国家码：+86 与 0086 写法归一到同一个东西
  if (/^0{0,2}86\d{11}$/.test(digits)) digits = digits.slice(digits.indexOf('86') + 2)
  return digits
}

export function isValidPhone(raw) {
  const s = String(raw || '').trim()
  if (!ALLOWED_CHARS.test(s)) return false
  return CN_MOBILE.test(normalizePhone(s))
}

/** 输入框实时兜底：把不该出现的字符剔掉，超出长度截断 */
export function filterPhoneInput(raw) {
  return String(raw || '').replace(/[^\d+\-()\s]/g, '').slice(0, 20)
}
