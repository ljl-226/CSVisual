import { EditPen, DataAnalysis, Connection, Cpu, Monitor, TrendCharts, Grid, Histogram, Compass, Share, Document, SetUp, Coffee, MagicStick, Files, Brush, Lightning, Coin } from '@element-plus/icons-vue'

/**
 * 可视化组件注册表（唯一来源）。
 *
 * 曾经这份表只是 VisPlayer.vue 里的一个局部常量，而 CourseDetail / Profile 又
 * 各自靠「route 是不是 /code/ 开头」去猜该显示「敲代码」还是「看动画」——
 * 猜错了就是一个点不动的按钮（有批知识点 route 是 NULL，却照样显示「看动画」，
 * 点下去等于 router.push(null)）。现在表抽到这儿，三处共用同一个事实来源。
 */
export const VIS_MAP = {

  // 数据结构与算法
  'linked-list': { comp: () => import('@/components/vis/ds/LinkedList.vue'), kid: 1 },
  'stack': { comp: () => import('@/components/vis/ds/Stack.vue'), kid: 2 },
  'queue': { comp: () => import('@/components/vis/ds/Queue.vue'), kid: 3 },
  'binary-tree': { comp: () => import('@/components/vis/ds/BinaryTree.vue'), kid: 4 },
  'bplus-tree': { comp: () => import('@/components/vis/ds/BPlusTree.vue'), kid: 5 },
  'quick-sort': { comp: () => import('@/components/vis/ds/QuickSort.vue'), kid: 6 },
  'merge-sort': { comp: () => import('@/components/vis/ds/MergeSort.vue'), kid: 7 },
  'graph-traversal': { comp: () => import('@/components/vis/ds/GraphTraversal.vue'), kid: 8 },
  // 计算机网络
  'tcp-handshake': { comp: () => import('@/components/vis/net/TcpHandshake.vue'), kid: 9, props: { mode: 'handshake' } },
  'tcp-waves': { comp: () => import('@/components/vis/net/TcpHandshake.vue'), kid: 10, props: { mode: 'waves' } },
  'ip-routing': { comp: () => import('@/components/vis/net/IpRouting.vue'), kid: 11 },
  'arp': { comp: () => import('@/components/vis/net/Arp.vue'), kid: 12 },
  'congestion': { comp: () => import('@/components/vis/net/CongestionControl.vue'), kid: 13 },
  // 操作系统
  'process-state': { comp: () => import('@/components/vis/os/ProcessState.vue'), kid: 14 },
  'scheduler': { comp: () => import('@/components/vis/os/Scheduler.vue'), kid: 15 },
  'page-replacement': { comp: () => import('@/components/vis/os/PageReplacement.vue'), kid: 16 },
  'deadlock': { comp: () => import('@/components/vis/os/Deadlock.vue'), kid: 17 },
  // 计算机组成原理
  'pipeline': { comp: () => import('@/components/vis/co/Pipeline.vue'), kid: 18 },
  'memory-hierarchy': { comp: () => import('@/components/vis/co/MemoryHierarchy.vue'), kid: 19 },
  'alu': { comp: () => import('@/components/vis/co/Alu.vue'), kid: 20 },
  'register-transfer': { comp: () => import('@/components/vis/co/RegisterTransfer.vue'), kid: 21 },
  // 高等数学
  'limit': { comp: () => import('@/components/vis/math/Limit.vue'), kid: 22 },
  'derivative': { comp: () => import('@/components/vis/math/Derivative.vue'), kid: 23 },
  'integral': { comp: () => import('@/components/vis/math/Integral.vue'), kid: 24 },
  // 线性代数
  'matrix-transform': { comp: () => import('@/components/vis/linalg/MatrixTransform.vue'), kid: 25 },
  'eigen-vector': { comp: () => import('@/components/vis/linalg/EigenVector.vue'), kid: 26 },
  // 概率论与数理统计
  'distribution': { comp: () => import('@/components/vis/prob/Distribution.vue'), kid: 27 },
  'central-limit': { comp: () => import('@/components/vis/prob/CentralLimit.vue'), kid: 28 },
  // 大学物理
  'projectile': { comp: () => import('@/components/vis/phys/Projectile.vue'), kid: 29 },
  'shm': { comp: () => import('@/components/vis/phys/SimpleHarmonic.vue'), kid: 30 },
  // 离散数学
  'truth-table': { comp: () => import('@/components/vis/dm/TruthTable.vue'), kid: 31 },
  'mst': { comp: () => import('@/components/vis/dm/MstPrim.vue'), kid: 32 },
  // 核心课补充
  'hash-table': { comp: () => import('@/components/vis/ds/HashTable.vue'), kid: 33 },
  'cache-mapping': { comp: () => import('@/components/vis/co/CacheMapping.vue'), kid: 34 },
  // 数据结构（教材对照补充）
  'doubly-linked': { comp: () => import('@/components/vis/ds/DoublyLinked.vue'), kid: 35 },
  'bst': { comp: () => import('@/components/vis/ds/Bst.vue'), kid: 36 },
  'heap-sort': { comp: () => import('@/components/vis/ds/HeapSort.vue'), kid: 37 },
  'dijkstra': { comp: () => import('@/components/vis/ds/Dijkstra.vue'), kid: 38 },
  'topological': { comp: () => import('@/components/vis/ds/Topological.vue'), kid: 39 },
  'binary-search': { comp: () => import('@/components/vis/ds/BinarySearch.vue'), kid: 40 },
  // 计算机网络（教材对照补充）
  'subnet': { comp: () => import('@/components/vis/net/Subnet.vue'), kid: 41 },
  'dns': { comp: () => import('@/components/vis/net/Dns.vue'), kid: 42 },
  'csma-cd': { comp: () => import('@/components/vis/net/CsmaCd.vue'), kid: 43 },
  'sliding-window': { comp: () => import('@/components/vis/net/SlidingWindow.vue'), kid: 44 },
  'encapsulation': { comp: () => import('@/components/vis/net/Encapsulation.vue'), kid: 45 },
  'routing-protocol': { comp: () => import('@/components/vis/net/RoutingProtocol.vue'), kid: 46 },
  // 操作系统（教材对照补充）
  'semaphore': { comp: () => import('@/components/vis/os/Semaphore.vue'), kid: 47 },
  'banker': { comp: () => import('@/components/vis/os/Banker.vue'), kid: 48 },
  'disk-scheduling': { comp: () => import('@/components/vis/os/DiskScheduling.vue'), kid: 49 },
  'paging-address': { comp: () => import('@/components/vis/os/PagingAddress.vue'), kid: 50 },
  // 计算机组成原理（教材对照补充）
  'float-ieee754': { comp: () => import('@/components/vis/co/FloatIeee754.vue'), kid: 51 },
  'addressing': { comp: () => import('@/components/vis/co/Addressing.vue'), kid: 52 },
  'bus-arbitration': { comp: () => import('@/components/vis/co/BusArbitration.vue'), kid: 53 },
  'instruction-cycle': { comp: () => import('@/components/vis/co/InstructionCycle.vue'), kid: 54 },
  // 高等数学（补充）
  'taylor': { comp: () => import('@/components/vis/math/Taylor.vue'), kid: 55 },
  'ode-field': { comp: () => import('@/components/vis/math/OdeField.vue'), kid: 56 },
  'gradient': { comp: () => import('@/components/vis/math/Gradient.vue'), kid: 57 },
  // 线性代数（补充）
  'gauss': { comp: () => import('@/components/vis/linalg/Gauss.vue'), kid: 58 },
  'determinant': { comp: () => import('@/components/vis/linalg/Determinant.vue'), kid: 59 },
  // 概率论（补充）
  'bayes': { comp: () => import('@/components/vis/prob/Bayes.vue'), kid: 60 },
  'law-large-numbers': { comp: () => import('@/components/vis/prob/LawLargeNumbers.vue'), kid: 61 },
  // 大学物理（补充）
  'incline': { comp: () => import('@/components/vis/phys/Incline.vue'), kid: 62 },
  'collision': { comp: () => import('@/components/vis/phys/Collision.vue'), kid: 63 },
  // 离散数学（补充）
  'venn': { comp: () => import('@/components/vis/dm/Venn.vue'), kid: 64 },
  'euler': { comp: () => import('@/components/vis/dm/Euler.vue'), kid: 65 },
  // 数学、统计与物理（扩展）
  'multivar': { comp: () => import('@/components/vis/math/Multivar.vue'), kid: 86 },
  'series': { comp: () => import('@/components/vis/math/Series.vue'), kid: 87 },
  'quadratic': { comp: () => import('@/components/vis/linalg/Quadratic.vue'), kid: 88 },
  'estimation': { comp: () => import('@/components/vis/prob/Estimation.vue'), kid: 89 },
  'hypothesis': { comp: () => import('@/components/vis/prob/Hypothesis.vue'), kid: 90 },
  'rigid-body': { comp: () => import('@/components/vis/phys/RigidBody.vue'), kid: 91 },
  'wave': { comp: () => import('@/components/vis/phys/Wave.vue'), kid: 92 }
}

/** name 有没有对应动画 */
export function hasVis(name) {
  return Object.prototype.hasOwnProperty.call(VIS_MAP, String(name || ''))
}

/** knowledge.route -> { label, icon, path }，没有动画或代码实验室时落到学概念 */
export function labOf(route, kid) {
  const r = String(route || '')
  if (r.startsWith('/code/')) {
    return { kind: 'code', label: '敲代码', icon: EditPen, path: r }
  }
  if (r.startsWith('/vis/')) {
    const name = r.slice('/vis/'.length)
    if (hasVis(name)) return { kind: 'vis', label: '看动画', icon: DataAnalysis, path: r }
  }
  return { kind: 'concept', label: '学概念', icon: Files, path: '/knowledge/' + kid }
}
