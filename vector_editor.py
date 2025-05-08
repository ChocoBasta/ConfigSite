import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QHBoxLayout, QLabel, QFileDialog,
                            QSpinBox, QGroupBox, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QPainterPath
import ezdxf
from profile_manager import ProfileManager

class DrawingArea(QWidget):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.setMinimumSize(800, 600)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set up coordinate system
        width = self.width()
        height = self.height()
        margin = 50
        print(f"\nDrawing area size: {width}x{height}")
        
        # Calculate scaling factors
        scale_x = (width - 2 * margin) / self.container.width
        scale_y = (height - 2 * margin) / self.container.height
        scale = min(scale_x, scale_y)
        print(f"Scale factors - X: {scale_x}, Y: {scale_y}, Using: {scale}")
        
        # Transform coordinates
        def transform(x, y):
            return (int(margin + x * scale), int(height - margin - y * scale))
        
        # Draw profile if available
        if self.container.current_profile:
            print("\nDrawing profile:")
            # Draw main profile sections
            for layer, points in self.container.current_profile.items():
                print(f"Layer {layer}: {len(points)} points")
                if points:
                    # Set color based on layer type
                    if 'SLOT' in layer:
                        painter.setPen(QPen(Qt.GlobalColor.red, 2))
                    else:
                        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
                    
                    # Draw the path
                    path = QPainterPath()
                    start_x, start_y = transform(points[0][0], points[0][1])
                    print(f"First point at ({points[0][0]}, {points[0][1]}) transforms to ({start_x}, {start_y})")
                    path.moveTo(start_x, start_y)
                    for x, y in points[1:]:
                        tx, ty = transform(x, y)
                        print(f"Point at ({x}, {y}) transforms to ({tx}, {ty})")
                        path.lineTo(tx, ty)
                    
                    # Close the path if it's not a slot
                    if not 'SLOT' in layer and len(points) > 2:
                        path.lineTo(start_x, start_y)
                    
                    painter.drawPath(path)
        else:
            print("No profile to draw")
        
        # Draw dimensions
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        
        # Width dimension
        x1, y1 = transform(0, 0)
        x2, y2 = transform(self.container.width, 0)
        painter.drawLine(x1, y1, x2, y2)
        painter.drawText(x1 + (x2 - x1)//2 - 30, y1 + 20, f"{self.container.width}mm")
        
        # Height dimension
        x1, y1 = transform(0, 0)
        x2, y2 = transform(0, self.container.height)
        painter.drawLine(x1, y1, x2, y2)
        painter.drawText(x1 - 60, y1 - (y1 - y2)//2, f"{self.container.height}mm")

class Container:
    def __init__(self):
        self.width = 400
        self.height = 600
        self.material_thickness = 18
        self.current_profile = None

    def update_dimensions(self, width, height, material):
        self.width = width
        self.height = height
        self.material_thickness = material

class VectorEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Config Editor")
        self.setMinimumSize(1000, 700)
        
        # Initialize container and profile manager
        self.container = Container()
        self.profile_manager = ProfileManager()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel (controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Profile selection
        profile_group = QGroupBox("Profile Selection")
        profile_layout = QVBoxLayout(profile_group)
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profile_manager.list_profiles())
        self.profile_combo.currentTextChanged.connect(self.update_profile)
        profile_layout.addWidget(QLabel("Select Profile:"))
        profile_layout.addWidget(self.profile_combo)
        
        left_layout.addWidget(profile_group)
        
        # Dimensions group
        dim_group = QGroupBox("Dimensions")
        dim_layout = QFormLayout(dim_group)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 2000)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" mm")
        self.width_spin.valueChanged.connect(self.update_dimensions)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 2000)
        self.height_spin.setValue(600)
        self.height_spin.setSuffix(" mm")
        self.height_spin.valueChanged.connect(self.update_dimensions)
        
        self.material_spin = QSpinBox()
        self.material_spin.setRange(1, 50)
        self.material_spin.setValue(18)
        self.material_spin.setSuffix(" mm")
        self.material_spin.valueChanged.connect(self.update_dimensions)
        
        dim_layout.addRow("Width:", self.width_spin)
        dim_layout.addRow("Height:", self.height_spin)
        dim_layout.addRow("Material Thickness:", self.material_spin)
        
        left_layout.addWidget(dim_group)
        
        # Export button
        export_btn = QPushButton("Export DXF")
        export_btn.clicked.connect(self.export_dxf)
        left_layout.addWidget(export_btn)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Drawing area
        self.drawing_area = DrawingArea(self.container)
        layout.addWidget(self.drawing_area, stretch=2)
        
        # Set initial profile if available
        if self.profile_combo.count() > 0:
            self.update_profile(self.profile_combo.currentText())

    def update_profile(self, profile_name):
        """Update the current profile based on selection"""
        if not profile_name:
            return
            
        print(f"\nUpdating profile to: {profile_name}")
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            print("No profile data found")
            return
            
        print(f"Setting profile with {len(profile)} layers")
        self.container.current_profile = profile
        self.drawing_area.update()

    def update_dimensions(self):
        """Update container dimensions and refresh display"""
        width = self.width_spin.value()
        height = self.height_spin.value()
        material = self.material_spin.value()
        
        self.container.update_dimensions(width, height, material)
        
        # Update current profile if one is selected
        profile_name = self.profile_combo.currentText()
        if profile_name:
            self.update_profile(profile_name)
        
        self.drawing_area.update()

    def export_dxf(self):
        """Export the current design to DXF"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export DXF",
            "",
            "DXF Files (*.dxf)"
        )
        
        if filepath:
            try:
                # Create new DXF document
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()
                
                # Get current profile
                profile_name = self.profile_combo.currentText()
                if not profile_name:
                    return
                    
                profile = self.profile_manager.get_profile(profile_name)
                if not profile:
                    return
                
                # Scale the profile
                scaled_profile = self.profile_manager.scale_profile(
                    profile_name,
                    self.container.width / 1000,  # Convert to meters
                    self.container.height / 1000,
                    self.container.material_thickness / 1000
                )
                
                # Add each layer to the DXF
                for layer, points in scaled_profile.items():
                    if points:
                        msp.add_lwpolyline(points, dxfattribs={'layer': layer})
                
                # Save the file
                doc.saveas(filepath)
                
            except Exception as e:
                print(f"Failed to export DXF: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = VectorEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 