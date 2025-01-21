import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget  # 修改这行
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt6.QtCore import QSize  # 添加这行导入

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 视角参数
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.zoom = -50.0
        self.lastPos = None
        self.generate_sample_data()
        
        # 添加鼠标灵敏度参数
        self.rotationSpeed = 0.5  # 旋转速度
        self.zoomSpeed = 1.0      # 缩放速度

    def generate_sample_data(self):
        # 生成随机点
        num_points = 700_000
        self.points = np.random.randn(num_points, 3).astype(np.float32)
        self.points *= 10  # 扩大显示范围
        
        # 生成一些随机线（连接相邻点）
        self.lines = self.points[::2]  # 取偶数位置的点作为线段起点
        self.lines_end = self.points[1::2]  # 取奇数位置的点作为线段终点

    # 删除这两个重复的方法
    # def minimumSizeHint(self):
    #     return (50, 50)
    # def sizeHint(self):
    #     return (800, 600)

    # 保留文件开头定义的这两个正确的方法
    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(800, 600)

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(1.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置视角
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.xRot, 1.0, 0.0, 0.0)
        glRotatef(self.yRot, 0.0, 1.0, 0.0)
        glRotatef(self.zRot, 0.0, 0.0, 1.0)

        # 绘制点
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)
        for point in self.points:
            glVertex3fv(point)
        glEnd()

        # 绘制线
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        for start, end in zip(self.lines, self.lines_end):
            glVertex3fv(start)
            glVertex3fv(end)
        glEnd()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        if self.lastPos is None:
            return
            
        dx = event.pos().x() - self.lastPos.x()
        dy = event.pos().y() - self.lastPos.y()

        # 左键拖动旋转
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.yRot += dx * self.rotationSpeed
            self.xRot += dy * self.rotationSpeed
            self.update()
        # 添加右键拖动平移
        elif event.buttons() & Qt.MouseButton.RightButton:
            self.xTrans = dx * 0.1
            self.yTrans = -dy * 0.1
            self.update()
        
        self.lastPos = event.pos()

    def wheelEvent(self, event):
        # 优化缩放体验
        zoomFactor = event.angleDelta().y() / 120.0
        self.zoom += zoomFactor * self.zoomSpeed
        # 限制缩放范围
        self.zoom = max(-100.0, min(-5.0, self.zoom))
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)
        self.setWindowTitle("大规模三维点云显示")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())