/**
 * 头像文件 → 压缩后的 Blob。
 *
 * 为什么在前端压而不是让后端压：
 * 一张手机随手拍 3-5MB，原样上传既慢又费流量；后端再怎么限也只是「报错让你自己压」，
 * 用户体验一样差。canvas 缩到 ≤512px、JPEG 0.85，一张头像 30-80KB，肉眼无损。
 * 后端的 2MB 限制保留着，是给「极端格式压缩失败走原图直传」兜底的。
 *
 * 为什么不用 createImageBitmap：Safari 旧版对 Blob 支持不全，Image + objectURL
 * 是兼容性最稳的一条路。
 */

/** 允许的输入类型。gif 虽然能动，但压完就成静帧了，不如一开始就排除 */
const ACCEPT_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export function isAvatarImage(file) {
  return file && ACCEPT_TYPES.includes(file.type)
}

export function compressAvatar(file, maxSide = 512, quality = 0.85) {
  return new Promise((resolve, reject) => {
    if (!isAvatarImage(file)) {
      reject(new Error('仅支持 jpg / png / webp 格式的图片'))
      return
    }
    const url = URL.createObjectURL(file)
    const img = new Image()
    const cleanup = () => URL.revokeObjectURL(url)

    img.onload = () => {
      try {
        // 只缩小不放大：小图硬拉到 512px 只会糊
        const scale = Math.min(1, maxSide / Math.max(img.width, img.height))
        const w = Math.max(1, Math.round(img.width * scale))
        const h = Math.max(1, Math.round(img.height * scale))
        const canvas = document.createElement('canvas')
        canvas.width = w
        canvas.height = h
        const ctx = canvas.getContext('2d')
        // 白底：透明 PNG 转成 JPEG 后不会变成黑块
        ctx.fillStyle = '#fff'
        ctx.fillRect(0, 0, w, h)
        ctx.drawImage(img, 0, 0, w, h)
        canvas.toBlob(
          blob => {
            cleanup()
            if (blob) resolve(blob)
            else reject(new Error('图片处理失败，请换一张试试'))
          },
          'image/jpeg',
          quality
        )
      } catch (e) {
        cleanup()
        reject(new Error('图片处理失败，请换一张试试'))
      }
    }
    img.onerror = () => {
      cleanup()
      reject(new Error('图片读取失败，文件可能已损坏'))
    }
    img.src = url
  })
}
