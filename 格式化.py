

import sys
import os
import configparser
import pyodbc
from PyQt6.QtWidgets import QApplication, QTableWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy, QMenu,QDateEdit
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QBrush, QFont, QIcon, QAction, QScreen  # 从 PyQt6.QtGui 导入 QScreen
from PySide6.QtUiTools import QUiLoader
import datetime
from PyQt6.QtCore import  QRect, Qt, QMargins,QDate, QPropertyAnimation, QEasingCurve

from PyQt6.QtWidgets import QSpacerItem, QSizePolicy


class DatabaseConnection:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.server = self.config.get('Database', 'ServerName')
        self.database = self.config.get('Database', 'Database')
        self.username_db = self.config.get('Database', 'LogId')
        self.password_db = self.config.get('Database', 'LOGPASS')

    def connect(self):
        try:
            conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username_db};PWD={self.password_db}'
            )
            return conn
        except pyodbc.Error as e:
            raise pyodbc.Error(f"数据库连接错误: {str(e)}")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LDM-ERP- 登录")
        self.setGeometry(100, 100, 300, 300)

        self.main_layout = QVBoxLayout()  # 主布局

        # 设置标签和输入框的字体为微软雅黑，字号 14，加粗，颜色为黑色
        label_font = QFont("微软雅黑", 14)
        label_font1 = QFont("微软雅黑", 12)

        label_font.setBold(True)
        label_palette = QPalette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))

        # 员工编号输入框及其标签
        self.employee_id_layout = QVBoxLayout()
        self.label_username = QLabel("员工编号:")
        self.label_username.setFont(label_font)
        self.label_username.setPalette(label_palette)
        self.edit_username = QLineEdit()
        self.edit_username.textChanged.connect(self.show_employee_name)
        # 绑定回车键按下事件
        self.edit_username.returnPressed.connect(self.move_to_password)
        self.edit_username.setFont(label_font)
        self.employee_id_layout.addWidget(self.label_username)
        self.employee_id_layout.addWidget(self.edit_username)
        # 员工名称及其标签
        self.employee_name_layout = QHBoxLayout()
        self.label_employee_name = QLabel("员工名称:")
        self.label_employee_name.setFont(label_font1)
        self.label_employee_name.setPalette(label_palette)
        self.employee_name_layout.addWidget(self.label_employee_name)

        # 添加水平间距
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.employee_name_layout.addItem(spacer)

        self.employee_id_layout.addLayout(self.employee_name_layout)
        self.main_layout.addLayout(self.employee_id_layout)
        # 设置布局的对齐方式为顶部对齐
        self.employee_id_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        # 密码输入框及其标签
        self.password_layout = QHBoxLayout()  # 使用 QHBoxLayout 而不是 QVBoxLayout
        self.label_password = QLabel("密码:")
        self.label_password.setFont(label_font)
        self.label_password.setPalette(label_palette)
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_password.setFont(label_font)
        self.password_layout.addWidget(self.label_password)
        self.password_layout.addWidget(self.edit_password)
        self.main_layout.addLayout(self.password_layout)
        # 为密码输入框及其标签添加垂直间距
        spacer_above_password = QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.main_layout.addItem(spacer_above_password)
        self.main_layout.addLayout(self.password_layout)

        # 设置布局的边距
        self.employee_id_layout.setContentsMargins(0, 10, 0, 0)  # 上、右、下、左
        self.employee_name_layout.setContentsMargins(0, 10, 0, 40)  # 上、右、下、左

        # 登录按钮
        self.button_login = QPushButton("登录")
        self.button_login.setFont(label_font)
        self.button_login.setPalette(label_palette)
        self.button_login.clicked.connect(self.login)
        self.main_layout.addWidget(self.button_login)

        self.setLayout(self.main_layout)

        self.employee_name = ""

        # 从 Config.ini 文件读取数据库连接信息
        self.read_config()

        # 加载背景图片
        self.background_image = QPixmap(os.path.join(os.getcwd(), "主登录图片.png"))
        # 将登录窗口移动到屏幕中心
        self.move_to_center()
        
        # 为密码输入框添加 returnPressed 信号处理，触发登录操作
        self.edit_password.returnPressed.connect(self.login)
        
    def move_to_center(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

    def read_config(self):
        config_file = os.path.join(os.getcwd(), "Config.ini")
        try:
            self.db_connection = DatabaseConnection(config_file)
        except configparser.NoSectionError:
            QMessageBox.critical(self, "配置文件错误", "Config.ini 文件中没有 Database 节，请检查文件内容。")
        except configparser.Error as e:
            QMessageBox.critical(self, "配置文件错误", f"读取 Config.ini 文件时发生错误: {str(e)}")
        except KeyError as e:
            QMessageBox.critical(self, "配置文件错误", f"Config.ini 文件中缺少键: {str(e)}")

    def show_employee_name(self):
        ygbh = self.edit_username.text()
        if ygbh:
            try:
                conn = self.db_connection.connect()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT ygmc FROM t_ygda WHERE ygbh =?", (ygbh,)
                )
                result = cursor.fetchone()
                if result:
                    self.employee_name = result[0]
                    print(f"Found employee name: {self.employee_name}")  # 打印找到的员工姓名
                    self.label_employee_name.setText(f"员工名称: {self.employee_name}")
                else:
                    self.employee_name = ""
                    print("No employee found")  # 打印未找到员工的信息
                    self.label_employee_name.setText("员工名称: 未找到")
                cursor.close()
                conn.close()
            except pyodbc.Error as e:
                print(f"Database error: {str(e)}")  # 打印详细的数据库错误信息
                self.employee_name = ""
                self.label_employee_name.setText("员工名称: 数据库错误")
        else:
            self.employee_name = ""
            self.label_employee_name.setText("员工名称:")

    def login(self):
        ygbh = self.edit_username.text()
        password = self.edit_password.text()
        if self.check_login(ygbh, password):
            QMessageBox.information(self, "登录成功", "登录成功！")
            self.open_menu_window()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误！")

    def check_login(self, ygbh, password):
        try:
            conn = self.db_connection.connect()
            cursor = conn.cursor()
            # 查询员工表，验证登录信息
            cursor.execute(
                "SELECT * FROM t_ygda WHERE ygbh =? AND mm =?", (ygbh, password)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                return True
            else:
                return False
        except pyodbc.Error as e:
            QMessageBox.critical(self, "数据库错误", f"数据库连接错误: {str(e)}")
            return False

    def open_menu_window(self):
        self.close()  # 关闭登录窗口
        self.menu_window = MenuWindow()  # 创建菜单窗口
        self.menu_window.show()  # 显示菜单窗口

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.background_image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)))
        painter.drawRect(self.rect())
    
    def move_to_password(self):
        self.edit_password.setFocus()

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("菜单")
        self.setGeometry(100, 100, 150, 600)

        # 设置主布局为垂直布局
        self.main_layout = QVBoxLayout()
        # 设置布局的全局间距为 5 像素
        self.main_layout.setSpacing(5)
        # 设置窗口的背景颜色为白色
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.setPalette(palette)

        # 设置按钮的字体为微软雅黑，字号 14，加粗，颜色为黑色
        button_font = QFont("微软雅黑", 14)
        button_font.setBold(True)
        button_palette = QPalette()
        button_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))

        # 基础管理按钮
        self.button_basic_management = QPushButton("基础管理")
        self.button_basic_management.setFont(button_font)
        self.button_basic_management.setPalette(button_palette)
        self.button_basic_management.setFixedWidth(100)  # 设置按钮宽度为 100
        self.button_basic_management.setStyleSheet(
            "QPushButton {"
            "    background-color: #4CAF50; "
            "    border: 2px solid #4CAF50; "
            "    border-radius: 5px; "
            "    color: white; "
            "    padding: 5px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #45a049; "
            "    border: 2px solid #45a049; "
            "}"
        )
        # 创建基础管理的子菜单
        basic_management_menu = QMenu(self)
        action_basic_1 = QAction("基础操作 1", self)
        action_basic_2 = QAction("基础操作 2", self)
        basic_management_menu.addAction(action_basic_1)
        basic_management_menu.addAction(action_basic_2)
        self.button_basic_management.setMenu(basic_management_menu)
        self.main_layout.addWidget(self.button_basic_management)


        # 仓库管理按钮
        self.button_warehouse_management = QPushButton("仓库管理")
        self.button_warehouse_management.setFont(button_font)
        self.button_warehouse_management.setPalette(button_palette)
        self.button_warehouse_management.setFixedWidth(100)  # 设置按钮宽度为 100
        self.button_warehouse_management.setStyleSheet(
            "QPushButton {"
            "    background-color: #2196F3; "
            "    border: 2px solid #2196F3; "
            "    border-radius: 5px; "
            "    color: white; "
            "    padding: 5px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #1e88e5; "
            "    border: 2px solid #1e88e5; "
            "}"
        )
        # 创建仓库管理的子菜单
        warehouse_menu = QMenu(self)
        action_shipment_query = QAction("发货查询", self)
        action_shipment_query.triggered.connect(self.open_shipment_query_window)
        action_reimbursement = QAction("个人报销", self)
        action_monthly_report = QAction("每月报表", self)
        action_weight_calculation = QAction("重量计算", self)
        action_product_info = QAction("产品资料", self)
        warehouse_menu.addAction(action_shipment_query)
        warehouse_menu.addAction(action_reimbursement)
        warehouse_menu.addAction(action_monthly_report)
        warehouse_menu.addAction(action_weight_calculation)
        warehouse_menu.addAction(action_product_info)
        self.button_warehouse_management.setMenu(warehouse_menu)
        self.main_layout.addWidget(self.button_warehouse_management)


        # 业务管理按钮
        self.button_business_management = QPushButton("业务管理")
        self.button_business_management.setFont(button_font)
        self.button_business_management.setPalette(button_palette)
        self.button_business_management.setFixedWidth(100)  # 设置按钮宽度为 100
        self.button_business_management.setStyleSheet(
            "QPushButton {"
            "    background-color: #FF9800; "
            "    border: 2px solid #FF9800; "
            "    border-radius: 5px; "
            "    color: white; "
            "    padding: 5px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #f57c00; "
            "    border: 2px solid #f57c00; "
            "}"
        )
        # 创建业务管理的子菜单
        business_management_menu = QMenu(self)
        action_business_1 = QAction("业务操作 1", self)
        action_business_2 = QAction("业务操作 2", self)
        business_management_menu.addAction(action_business_1)
        business_management_menu.addAction(action_business_2)
        self.button_business_management.setMenu(business_management_menu)
        self.main_layout.addWidget(self.button_business_management)


        # 人事管理按钮
        self.button_hr_management = QPushButton("人事管理")
        self.button_hr_management.setFont(button_font)
        self.button_hr_management.setPalette(button_palette)
        self.button_hr_management.setFixedWidth(100)  # 设置按钮宽度为 100
        self.button_hr_management.setStyleSheet(
            "QPushButton {"
            "    background-color: #9C27B0; "
            "    border: 2px solid #9C27B0; "
            "    border-radius: 5px; "
            "    color: white; "
            "    padding: 5px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #8e24aa; "
            "    border: 2px solid #8e24aa; "
            "}"
        )
        # 创建人事管理的子菜单
        hr_management_menu = QMenu(self)
        action_hr_1 = QAction("人事操作 1", self)
        action_hr_2 = QAction("人事操作 2", self)
        hr_management_menu.addAction(action_hr_1)
        hr_management_menu.addAction(action_hr_2)
        self.button_hr_management.setMenu(hr_management_menu)
        self.main_layout.addWidget(self.button_hr_management)


        # 调整布局的左边距
        self.main_layout.setContentsMargins(20, 0, 0, 0)



        self.setLayout(self.main_layout)

    def open_shipment_query_window(self):
        try:
            # 创建发货查询窗口
            self.shipment_query_window = QWidget()
            self.shipment_query_window.setWindowTitle("发货查询")
            # 获取屏幕尺寸
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            width = int(screen_geometry.width() * 3 / 4)
            height = int(screen_geometry.height() * 2 / 3)
            x = (screen_geometry.width() - width) // 2
            y = (screen_geometry.height() - height) // 2
            self.shipment_query_window.setGeometry(x, y, width, height)
            # 为发货查询窗口添加布局
            main_layout = QVBoxLayout()
            self.shipment_query_window.setLayout(main_layout)
            # 设置窗口的背景颜色为白色
            palette = self.shipment_query_window.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
            self.shipment_query_window.setPalette(palette)
            # 设置标签字体为黑色
            label_palette = self.shipment_query_window.palette()
            label_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)

            # 第一排
            first_row_layout = QHBoxLayout()
            label_start_date = QLabel("开始日期")
            label_start_date.setPalette(label_palette)  # 设置标签字体为黑色
            label_end_date = QLabel("结束日期")
            label_end_date.setPalette(label_palette)  # 设置标签字体为黑色
            button_query = self.create_animated_button("查询", "#FF5733")  # 为每个按钮设置不同的颜色
            button_print_label = self.create_animated_button("打印标签", "#33FF57")
            button_edit_save = self.create_animated_button("编辑后保存", "#5733FF")
            button_export_excel = self.create_animated_button("导出到EXCEL", "#FF33A1")
            button_print = self.create_animated_button("打印", "#33A1FF")
            button_product_inventory = self.create_animated_button("产品进销存", "#A1FF33")
            button_clear_filter = self.create_animated_button("清除筛选", "#FFA133")

            date_edit_start = QDateEdit()
            # 设置日期框控件1的日期为当前日期的60天前日期
            current_date = QDate.currentDate()
            date_60_days_ago = current_date.addDays(-60)
            date_edit_start.setDate(date_60_days_ago)
            date_edit_start.setFixedSize(150, 22)
            date_edit_start.setFont(QFont("Arial", 15))  # 设置日期控件字体大小为 10
            date_edit_start.setFixedSize(200, 35)
            date_edit_start.animation = QPropertyAnimation(date_edit_start, b"geometry")
            date_edit_start.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            date_edit_start.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            date_edit_start.enterEvent = lambda event: self.animate_widget(date_edit_start, 1.1)  # 鼠标进入时放大
            date_edit_start.leaveEvent = lambda event: self.animate_widget(date_edit_start, 1.0)  # 鼠标离开时恢复原大小
            date_edit_start.animation.finished.connect(lambda: self.reset_widget_size(date_edit_start))  # 动画结束后重置控件大小

            date_edit_end = QDateEdit()
            # 设置日期框控件2的日期为当前日期
            date_edit_end.setDate(current_date)
            date_edit_end.setFixedSize(150, 22)
            date_edit_end.setFont(QFont("Arial", 15))  # 设置日期控件字体大小为 10
            date_edit_end.setFixedSize(200, 35) 
            date_edit_end.animation = QPropertyAnimation(date_edit_end, b"geometry")
            date_edit_end.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            date_edit_end.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            date_edit_end.enterEvent = lambda event: self.animate_widget(date_edit_end, 1.1)  # 鼠标进入时放大
            date_edit_end.leaveEvent = lambda event: self.animate_widget(date_edit_end, 1.0)  # 鼠标离开时恢复原大小
            date_edit_end.animation.finished.connect(lambda: self.reset_widget_size(date_edit_end))  # 动画结束后重置控件大小

            # 先添加一个拉伸项，将后续元素推到右侧
            #first_row_layout.addStretch(1)
            first_row_layout.addWidget(label_start_date)
            first_row_layout.addWidget(date_edit_start)
            first_row_layout.addWidget(label_end_date)
            first_row_layout.addWidget(date_edit_end)
            first_row_layout.addWidget(button_query)
            first_row_layout.addWidget(button_print_label)
            first_row_layout.addWidget(button_edit_save)
            first_row_layout.addWidget(button_export_excel)
            first_row_layout.addWidget(button_print)
            first_row_layout.addWidget(button_product_inventory)
            first_row_layout.addWidget(button_clear_filter)
         
             # 调整第一排元素的位置
            #self.move_first_row_left(first_row_layout, 300)
            main_layout.addLayout(first_row_layout)
            # 第二排
            second_row_layout = QHBoxLayout()
            label_color = QLabel("颜色")
            label_color.setPalette(label_palette)  # 设置标签字体为黑色
            text_input_color = QLineEdit()
            text_input_color.setStyleSheet("background-color: white;")  # 设置输入框为白色
            text_input_color.setFixedSize(200, 40)  # 设置文本输入框大小
            text_input_color.animation = QPropertyAnimation(text_input_color, b"geometry")
            text_input_color.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            text_input_color.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            text_input_color.enterEvent = lambda event: self.animate_widget(text_input_color, 1.1)  # 鼠标进入时放大
            text_input_color.leaveEvent = lambda event: self.animate_widget(text_input_color, 1.0)  # 鼠标离开时恢复原大小
            text_input_color.animation.finished.connect(lambda: self.reset_widget_size(text_input_color))  # 动画结束后重置控件大小

            label_customer_color = QLabel("客户颜色")
            label_customer_color.setPalette(label_palette)  # 设置标签字体为黑色
            text_input_customer_color = QLineEdit()
            text_input_customer_color.setStyleSheet("background-color: white;")  # 设置输入框为白色
            text_input_customer_color.setFixedSize(200, 40)  # 设置文本输入框大小
            text_input_customer_color.animation = QPropertyAnimation(text_input_customer_color, b"geometry")
            text_input_customer_color.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            text_input_customer_color.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            text_input_customer_color.enterEvent = lambda event: self.animate_widget(text_input_customer_color, 1.1)  # 鼠标进入时放大
            text_input_customer_color.leaveEvent = lambda event: self.animate_widget(text_input_customer_color, 1.0)  # 鼠标离开时恢复原大小
            text_input_customer_color.animation.finished.connect(lambda: self.reset_widget_size(text_input_customer_color))  # 动画结束后重置控件大小

            label_surface_treatment = QLabel("表面处理")
            label_surface_treatment.setPalette(label_palette)  # 设置标签字体为黑色
            text_input_surface_treatment = QLineEdit()
            text_input_surface_treatment.setStyleSheet("background-color: white;")  # 设置输入框为白色
            text_input_surface_treatment.setFixedSize(200, 40)  # 设置文本输入框大小
            text_input_surface_treatment.animation = QPropertyAnimation(text_input_surface_treatment, b"geometry")
            text_input_surface_treatment.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            text_input_surface_treatment.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            text_input_surface_treatment.enterEvent = lambda event: self.animate_widget(text_input_surface_treatment, 1.1)  # 鼠标进入时放大
            text_input_surface_treatment.leaveEvent = lambda event: self.animate_widget(text_input_surface_treatment, 1.0)  # 鼠标离开时恢复原大小
            text_input_surface_treatment.animation.finished.connect(lambda: self.reset_widget_size(text_input_surface_treatment))  # 动画结束后重置控件大小
            second_row_layout.addWidget(label_color)
            second_row_layout.addWidget(text_input_color)
            second_row_layout.addWidget(label_customer_color)
            second_row_layout.addWidget(text_input_customer_color)
            second_row_layout.addWidget(label_surface_treatment)
            second_row_layout.addWidget(text_input_surface_treatment)
            second_row_layout.addStretch(1)  # 弹性空间
            main_layout.addLayout(second_row_layout)

            # 第三排
            third_row_layout = QHBoxLayout()
            label_specification = QLabel("规格")
            label_specification.setPalette(label_palette)  # 设置标签字体为黑色
            text_input_specification = QLineEdit()
            text_input_specification.setStyleSheet("background-color: white;")  # 设置输入框为白色
            text_input_specification.setFixedSize(200, 40)  # 设置文本输入框大小
            text_input_specification.animation = QPropertyAnimation(text_input_specification, b"geometry")
            text_input_specification.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            text_input_specification.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            text_input_specification.enterEvent = lambda event: self.animate_widget(text_input_specification, 1.1)  # 鼠标进入时放大
            text_input_specification.leaveEvent = lambda event: self.animate_widget(text_input_specification, 1.0)  # 鼠标离开时恢复原大小
            text_input_specification.animation.finished.connect(lambda: self.reset_widget_size(text_input_specification))  # 动画结束后重置控件大小

            label_customer_name = QLabel("客户名称")
            label_customer_name.setPalette(label_palette)  # 设置标签字体为黑色
            text_input_customer_name = QLineEdit()
            text_input_customer_name.setStyleSheet("background-color: white;")  # 设置输入框为白色
            text_input_customer_name.setFixedSize(200, 40)  # 设置文本输入框大小
            text_input_customer_name.animation = QPropertyAnimation(text_input_customer_name, b"geometry")
            text_input_customer_name.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            text_input_customer_name.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            text_input_customer_name.enterEvent = lambda event: self.animate_widget(text_input_customer_name, 1.1)  # 鼠标进入时放大
            text_input_customer_name.leaveEvent = lambda event: self.animate_widget(text_input_customer_name, 1.0)  # 鼠标离开时恢复原大小
            text_input_customer_name.animation.finished.connect(lambda: self.reset_widget_size(text_input_customer_name))  # 动画结束后重置控件大小

            label_bottom_color = QLabel("底料颜色")
            label_bottom_color.setPalette(label_palette)  # 设置标签字体为黑色
            text_input_bottom_color = QLineEdit()
            text_input_bottom_color.setStyleSheet("background-color: white;")  # 设置输入框为白色
            text_input_bottom_color.setFixedSize(200, 40)  # 设置文本输入框大小
            text_input_bottom_color.animation = QPropertyAnimation(text_input_bottom_color, b"geometry")
            text_input_bottom_color.animation.setDuration(100)  # 动画持续时间，单位：毫秒
            text_input_bottom_color.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
            text_input_bottom_color.enterEvent = lambda event: self.animate_widget(text_input_bottom_color, 1.1)  # 鼠标进入时放大
            text_input_bottom_color.leaveEvent = lambda event: self.animate_widget(text_input_bottom_color, 1.0)  # 鼠标离开时恢复原大小
            text_input_bottom_color.animation.finished.connect(lambda: self.reset_widget_size(text_input_bottom_color))  # 动画结束后重置控件大小
            
            third_row_layout.addWidget(label_specification)
            third_row_layout.addWidget(text_input_specification)
            third_row_layout.addWidget(label_customer_name)
            third_row_layout.addWidget(text_input_customer_name)
            third_row_layout.addWidget(label_bottom_color)
            third_row_layout.addWidget(text_input_bottom_color)
            third_row_layout.addStretch(1)  # 弹性空间
            main_layout.addLayout(third_row_layout)

            # 创建表格显示从 SQL 查询过来的内容
            table = QTableWidget()
            table.setColumnCount(20)
            main_layout.addWidget(table)

            self.shipment_query_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开发货查询窗口时发生错误: {str(e)}")

    def create_animated_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(
            f"QPushButton {{"
            f"    background-color: {color}; "
            "    border: 2px solid; "
            "    border-radius: 5px; "
            "    color: white; "
            "    padding: 5px;"
            "    font-weight: normal;"
            "}"
            "QPushButton:hover {"
            "    background-color: gray; "  # 鼠标悬停时背景色为灰色
            "    color: black; "  # 鼠标悬停时字体为黑色
            "    font-weight: bold; "  # 鼠标悬停时字体加粗
            "    border: 2px solid gray; "  # 鼠标悬停时边框颜色为灰色
            "}"
        )
        button.animation = QPropertyAnimation(button, b"geometry")
        button.animation.setDuration(100)  # 动画持续时间，单位：毫秒
        button.animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 缓动曲线，使动画更平滑
        button.enterEvent = lambda event: self.animate_button(button, 1.1)  # 鼠标进入时放大
        button.leaveEvent = lambda event: self.animate_button(button, 1.0)  # 鼠标离开时恢复原大小
        button.animation.finished.connect(lambda: self.reset_button_size(button))  # 动画结束后重置按钮大小
        return button

    def animate_button(self, button, scale):
        original_size = button.geometry()
        new_size = QRect(
            original_size.x() ,  # 调整 x 坐标，防止按钮向右移动
            original_size.y() ,  # 调整 y 坐标，防止按钮向下移动
            int(original_size.width() * scale),
            int(original_size.height() * scale)
        )
        button.animation.setStartValue(original_size)
        button.animation.setEndValue(new_size)
        button.animation.start()
    
    def reset_button_size(self, button):
        button.setGeometry(button.animation.startValue())  # 重置按钮大小为动画开始时的尺寸

    def animate_widget(self, widget, scale):
        original_size = widget.geometry()
        new_size = QRect(
            original_size.x() - 5,  # 调整 x 坐标，防止控件向右移动
            original_size.y() - 5,  # 调整 y 坐标，防止控件向下移动
            int(original_size.width() * scale),
            int(original_size.height() * scale)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置应用程序图标
    app.setWindowIcon(QIcon(os.path.join(os.getcwd(), "LOGO.ico")))
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())