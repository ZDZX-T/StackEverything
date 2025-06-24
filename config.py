LANGUAGE = 'zh-cn'  # 语言，只能选择i18n文件夹内的json文件名称

PIC_PATH = 'user_image'
SERVER_PORT = 8456  # 服务使用的端口
SERVER_HOST = '0.0.0.0'  # 0.0.0.0使得外界可访问，如果仅本机使用，则替换为127.0.0.1
SERVER_DEBUG = False

LOG_RETENTION_TIME = 30  # 日志保留天数
SINGLE_LOG_MAX_LEN = 200  # 单条POST请求日志最大记录字节（防图片数据）

LONG_PRESS_THRESHOLD = 600  # item长按阈值，单位ms
DRAG_THRESHOLE = 400  # 拖拽阈值，必须要拖拽超过这个时间才会被认为是有效拖拽，单位ms
PIC_WIDTH_RATIO = 0.8  # 操作界面item图片宽度占比
PIC_DRAGING_ZOOM_RATIO = 0.6  # 操作界面拖拽时图片缩放比率
TRIGGER_INCLUSION_RATIO = 0.6  # 触发纳入的宽度百分比，例如值为0.6，元素大小为100，则左右两侧20px会触发排序，中间60px会触发移入
PIC_WIDTH_MAX = 1600  # 原图边长像素数（可在前端选择是否启用）
PIC_QUALITY = 0.8  # 原图图片质量（可在前端选择是否启用）
PIC_SM_WIDTH = 200  # 缩略图边长像素数
SCROLL_SAFE_ZONE_COLOR = '#f1f1f1'  # 滚动安全区颜色
MAX_BACK_FORWARD_STACK = 20  # 前进后退栈最大容量
AUTO_SCROLL_MAX_SPEED = 10  # 自动滚动最大速度，当拖拽物品到边缘时将触发自动滚动