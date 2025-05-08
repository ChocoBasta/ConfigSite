import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QHBoxLayout, QLabel, QFileDialog,
                            QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout,
                            QTabWidget)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Layout
from ezdxf.entities import Line, Text

class StorageContainer:
    def __init__(self):
        # Main dimensions (mm)
        self.total_width = 400
        self.total_height = 600
        self.total_depth = 200
        self.material_thickness = 9  # mm (plywood thickness)
        self.rotation = [30, 30, 0]  # rotation angles for x, y, z

    def get_dimensions(self):
        return {
            'width': self.total_width,
            'height': self.total_height,
            'depth': self.total_depth,
            'material_thickness': self.material_thickness
        }
    
    def calculate_panel_dimensions(self):
        t = self.material_thickness
        
        # Calculate actual panel sizes
        panels = {
            'LEFTRIGHT': {
                'width': self.total_depth,
                'height': self.total_height,
                'quantity': 2,
                'cutlines': {
                    'horizontal': [t, self.total_height - t],  # Top and bottom panel intersections
                    'vertical': [t, self.total_depth - t]  # Front and back panel intersections
                }
            },
            'FRONTBACK': {
                'width': self.total_width - (2 * t),  # Account for left/right panels
                'height': self.total_height,
                'quantity': 2,
                'cutlines': {
                    'horizontal': [t, self.total_height - t],  # Top and bottom panel intersections
                    'vertical': [0, self.total_width - (2 * t)]  # Full width since it's between side panels
                }
            },
            'BOTTOM': {
                'width': self.total_width,
                'height': self.total_depth,
                'quantity': 1,
                'cutlines': {
                    'horizontal': [0, self.total_depth],  # Full depth
                    'vertical': [t, self.total_width - t]  # Account for left/right panels
                }
            }
        }
        return panels

class Preview3D(QOpenGLWidget):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.last_pos = None
        self.setMinimumSize(600, 400)
        
        # Start rotation animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # 50ms = 20fps

    def rotate(self):
        self.container.rotation[1] += 1  # Rotate around Y axis
        self.update()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos is not None:
            dx = event.pos().x() - self.last_pos.x()
            dy = event.pos().y() - self.last_pos.y()
            self.container.rotation[0] += dy
            self.container.rotation[1] += dx
            self.last_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_pos = None

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 2000.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Move camera back to see the box
        glTranslatef(0, 0, -1000)
        
        # Rotate the scene
        glRotatef(self.container.rotation[0], 1, 0, 0)
        glRotatef(self.container.rotation[1], 0, 1, 0)
        glRotatef(self.container.rotation[2], 0, 0, 1)
        
        # Get dimensions and panel calculations
        dims = self.container.get_dimensions()
        panels = self.container.calculate_panel_dimensions()
        w = dims['width']
        h = dims['height']
        d = dims['depth']
        t = dims['material_thickness']
        
        # Center the container
        glTranslatef(-w/2, -h/2, -d/2)
        
        # Set material properties for plywood
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.4, 0.2, 0.0, 1.0])  # Brown wood color
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.4, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 5.0)
        
        # Draw bottom panel
        bottom = panels['BOTTOM']
        self.draw_panel([0, 0, 0], [bottom['width'], t, bottom['height']])
        
        # Draw left panel
        left = panels['LEFTRIGHT']
        self.draw_panel([0, t, 0], [t, left['height']-2*t, left['width']])
        
        # Draw right panel
        self.draw_panel([w-t, t, 0], [t, left['height']-2*t, left['width']])
        
        # Draw back panel
        front = panels['FRONTBACK']
        self.draw_panel([t, t, 0], [front['width'], front['height']-2*t, t])
        
        # Draw front panel (slightly transparent to see inside)
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.4, 0.2, 0.0, 0.5])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.4, 0.0, 0.5])
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.draw_panel([t, t, d-t], [front['width'], front['height']-2*t, t])
        glDisable(GL_BLEND)

    def draw_panel(self, pos, size):
        x, y, z = pos
        w, h, d = size
        
        glBegin(GL_QUADS)
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(x, y, z + d)
        glVertex3f(x + w, y, z + d)
        glVertex3f(x + w, y + h, z + d)
        glVertex3f(x, y + h, z + d)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(x, y, z)
        glVertex3f(x, y + h, z)
        glVertex3f(x + w, y + h, z)
        glVertex3f(x + w, y, z)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(x, y + h, z)
        glVertex3f(x, y + h, z + d)
        glVertex3f(x + w, y + h, z + d)
        glVertex3f(x + w, y + h, z)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(x, y, z)
        glVertex3f(x + w, y, z)
        glVertex3f(x + w, y, z + d)
        glVertex3f(x, y, z + d)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(x + w, y, z)
        glVertex3f(x + w, y + h, z)
        glVertex3f(x + w, y + h, z + d)
        glVertex3f(x + w, y, z + d)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(x, y, z)
        glVertex3f(x, y, z + d)
        glVertex3f(x, y + h, z + d)
        glVertex3f(x, y + h, z)
        glEnd()

class VectorEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VectorConfig - Storage Container Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create container instance
        self.container = StorageContainer()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Create dimension controls
        dimensions_group = QGroupBox("Container Dimensions")
        dimensions_layout = QFormLayout()
        
        # Width control
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(100, 1000)
        self.width_spin.setValue(self.container.total_width)
        self.width_spin.setSuffix(" mm")
        self.width_spin.valueChanged.connect(self.update_dimensions)
        dimensions_layout.addRow("Width:", self.width_spin)
        
        # Height control
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(100, 1000)
        self.height_spin.setValue(self.container.total_height)
        self.height_spin.setSuffix(" mm")
        self.height_spin.valueChanged.connect(self.update_dimensions)
        dimensions_layout.addRow("Height:", self.height_spin)
        
        # Depth control
        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(100, 1000)
        self.depth_spin.setValue(self.container.total_depth)
        self.depth_spin.setSuffix(" mm")
        self.depth_spin.valueChanged.connect(self.update_dimensions)
        dimensions_layout.addRow("Depth:", self.depth_spin)
        
        # Material thickness control
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(3, 50)
        self.thickness_spin.setValue(self.container.material_thickness)
        self.thickness_spin.setSuffix(" mm")
        self.thickness_spin.valueChanged.connect(self.update_dimensions)
        dimensions_layout.addRow("Material Thickness:", self.thickness_spin)
        
        dimensions_group.setLayout(dimensions_layout)
        left_layout.addWidget(dimensions_group)
        
        # Add export button
        self.export_button = QPushButton("Export DXF")
        self.export_button.clicked.connect(self.export_dxf)
        left_layout.addWidget(self.export_button)
        
        # Add stretch to push controls to the top
        left_layout.addStretch()
        
        # Add left panel to main layout
        layout.addWidget(left_panel, stretch=1)
        
        # Create tab widget for 2D and 3D views
        tab_widget = QTabWidget()
        
        # Create drawing areas
        self.drawing_area_2d = DrawingArea(self.container)
        self.drawing_area_3d = Preview3D(self.container)
        
        # Add views to tabs
        tab_widget.addTab(self.drawing_area_2d, "2D View")
        tab_widget.addTab(self.drawing_area_3d, "3D Preview")
        
        # Add tab widget to main layout
        layout.addWidget(tab_widget, stretch=3)
        
        # Status bar
        self.statusBar().showMessage("Ready")

    def update_dimensions(self):
        self.container.total_width = self.width_spin.value()
        self.container.total_height = self.height_spin.value()
        self.container.total_depth = self.depth_spin.value()
        self.container.material_thickness = self.thickness_spin.value()
        self.drawing_area_2d.update()
        self.drawing_area_3d.update()

    def export_dxf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save DXF", "", "DXF files (*.dxf)")
        if filename:
            if not filename.endswith('.dxf'):
                filename += '.dxf'
            
            # Create new DXF document
            doc = ezdxf.new()
            msp = doc.modelspace()

            # Calculate panel dimensions
            panels = self.container.calculate_panel_dimensions()
            
            # Current Y position for layout
            current_y = 0
            spacing = 20  # mm spacing between panels
            
            for panel_name, panel_data in panels.items():
                # Create layers for this panel
                panel_layer = panel_name
                slot_layer = f"{panel_name}_SLOT"
                cutline_x_layer = f"{panel_name}_XCUTLINE"
                cutline_y_layer = f"{panel_name}_YCUTLINE"
                
                # Create layers in DXF
                doc.layers.add(panel_layer)
                doc.layers.add(slot_layer)
                doc.layers.add(cutline_x_layer)
                doc.layers.add(cutline_y_layer)
                
                # Draw panel outline
                width = panel_data['width']
                height = panel_data['height']
                
                # Draw the panel outline
                points = [
                    (0, current_y),
                    (width, current_y),
                    (width, current_y + height),
                    (0, current_y + height),
                    (0, current_y)
                ]
                msp.add_lwpolyline(points, dxfattribs={'layer': panel_layer})
                
                # Add horizontal cutlines
                for x in panel_data['cutlines']['horizontal']:
                    points = [(0, current_y + x), (width, current_y + x)]
                    msp.add_lwpolyline(points, dxfattribs={'layer': cutline_x_layer})
                
                # Add vertical cutlines
                for y in panel_data['cutlines']['vertical']:
                    points = [(y, current_y), (y, current_y + height)]
                    msp.add_lwpolyline(points, dxfattribs={'layer': cutline_y_layer})
                
                # Move Y position for next panel
                current_y += height + spacing
            
            # Save the DXF file
            doc.saveas(filename)
            
            # Inform user
            self.statusBar().showMessage(f"Saved DXF to {filename}", 3000)

class DrawingArea(QWidget):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: white;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.PenStyle.SolidLine))
        
        # Get container dimensions
        dims = self.container.get_dimensions()
        
        # Calculate scale to fit in drawing area
        scale = min(
            (self.width() - 40) / dims['width'],
            (self.height() - 40) / dims['height']
        )
        
        # Calculate drawing position (centered)
        x_offset = int((self.width() - dims['width'] * scale) / 2)
        y_offset = int((self.height() - dims['height'] * scale) / 2)
        
        # Draw container outline
        painter.drawRect(
            x_offset,
            y_offset,
            int(dims['width'] * scale),
            int(dims['height'] * scale)
        )
        
        # Draw material thickness
        thickness = int(dims['material_thickness'] * scale)
        painter.drawRect(
            x_offset + thickness,
            y_offset + thickness,
            int((dims['width'] - 2 * thickness) * scale),
            int((dims['height'] - 2 * thickness) * scale)
        )

def main():
    app = QApplication(sys.argv)
    window = VectorEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 