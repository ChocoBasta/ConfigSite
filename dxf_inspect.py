import ezdxf
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton)
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PanelScaler:
    def __init__(self, original_panels):
        self.original_panels = original_panels
        self.scale_factors = {
            'width': 1.0,
            'height': 1.0,
            'depth': 1.0
        }
    
    def scale_panel(self, panel_name, panel_data):
        """Scale a panel based on cutlines and new dimensions"""
        # Get original dimensions
        original_width = max(x for x, _ in panel_data['outline']) - min(x for x, _ in panel_data['outline'])
        original_height = max(y for _, y in panel_data['outline']) - min(y for _, y in panel_data['outline'])
        
        # Calculate new dimensions
        if 'LEFTRIGHT' in panel_name:
            new_width = original_width * self.scale_factors['depth']
            new_height = original_height * self.scale_factors['height']
        elif 'FRONTBACK' in panel_name:
            new_width = original_width * self.scale_factors['width']
            new_height = original_height * self.scale_factors['height']
        else:  # BOTTOM
            new_width = original_width * self.scale_factors['width']
            new_height = original_height * self.scale_factors['depth']
        
        # Scale the outline
        min_x = min(x for x, _ in panel_data['outline'])
        min_y = min(y for _, y in panel_data['outline'])
        
        scaled_outline = []
        for x, y in panel_data['outline']:
            # Normalize coordinates
            norm_x = (x - min_x) / original_width
            norm_y = (y - min_y) / original_height
            # Scale
            new_x = min_x + (norm_x * new_width)
            new_y = min_y + (norm_y * new_height)
            scaled_outline.append((new_x, new_y))
        
        # Scale slots and cutlines
        scaled_slots = []
        for slot in panel_data.get('slots', []):
            scaled_slot = []
            for x, y in slot:
                norm_x = (x - min_x) / original_width
                norm_y = (y - min_y) / original_height
                new_x = min_x + (norm_x * new_width)
                new_y = min_y + (norm_y * new_height)
                scaled_slot.append((new_x, new_y))
            scaled_slots.append(scaled_slot)
        
        scaled_cutlines = []
        for cutline in panel_data.get('cutlines', []):
            scaled_cutline = []
            for x, y in cutline:
                norm_x = (x - min_x) / original_width
                norm_y = (y - min_y) / original_height
                new_x = min_x + (norm_x * new_width)
                new_y = min_y + (norm_y * new_height)
                scaled_cutline.append((new_x, new_y))
            scaled_cutlines.append(scaled_cutline)
        
        return {
            'outline': scaled_outline,
            'slots': scaled_slots,
            'cutlines': scaled_cutlines
        }

class DXFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DXF Panel Scaler")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add dimension controls
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(100, 2000)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" mm")
        self.width_spin.valueChanged.connect(self.update_scaling)
        left_layout.addWidget(QLabel("Width:"))
        left_layout.addWidget(self.width_spin)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(100, 2000)
        self.height_spin.setValue(600)
        self.height_spin.setSuffix(" mm")
        self.height_spin.valueChanged.connect(self.update_scaling)
        left_layout.addWidget(QLabel("Height:"))
        left_layout.addWidget(self.height_spin)
        
        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(100, 2000)
        self.depth_spin.setValue(200)
        self.depth_spin.setSuffix(" mm")
        self.depth_spin.valueChanged.connect(self.update_scaling)
        left_layout.addWidget(QLabel("Depth:"))
        left_layout.addWidget(self.depth_spin)
        
        # Add export button
        export_button = QPushButton("Export DXF")
        export_button.clicked.connect(self.export_dxf)
        left_layout.addWidget(export_button)
        
        # Add stretch to push controls to the top
        left_layout.addStretch()
        
        # Add left panel to main layout
        layout.addWidget(left_panel, stretch=1)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, stretch=3)
        
        # Load DXF file
        self.load_dxf()
        
        # Initialize panel scaler
        self.panel_scaler = PanelScaler(self.panels)
        
        # Initial plot
        self.update_plot()
    
    def load_dxf(self):
        # Path to your DXF file
        dxf_path = "simplefied.dxf"
        if not os.path.exists(dxf_path):
            dxf_path = r"c:\Users\samjk\Desktop\simplefied.dxf"
        
        if not os.path.exists(dxf_path):
            print(f"Error: Could not find DXF file at {dxf_path}")
            sys.exit(1)
        
        # Load DXF file
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # Initialize panels dictionary
        self.panels = {}
        
        # Load panels
        for panel_name in ["LEFTRIGHT", "FRONTBACK", "BOTTOM"]:
            panel_data = {'outline': [], 'slots': [], 'cutlines': []}
            
            # Get panel outline
            for entity in msp.query(f'POLYLINE[layer=="{panel_name}"]'):
                panel_data['outline'] = self.get_polyline_coords(entity)
            
            # Get slots
            slot_layer = f"{panel_name}_SLOT5_5"
            for entity in msp.query(f'POLYLINE[layer=="{slot_layer}"]'):
                panel_data['slots'].append(self.get_polyline_coords(entity))
            
            # Get cutlines
            for direction in ['X', 'Y']:
                cutline_layer = f"{panel_name}_{direction}CUTLINE"
                for entity in msp.query(f'POLYLINE[layer=="{cutline_layer}"]'):
                    panel_data['cutlines'].append(self.get_polyline_coords(entity))
            
            self.panels[panel_name] = panel_data
    
    def get_polyline_coords(self, entity):
        coords = []
        if entity.dxftype() == 'POLYLINE':
            for v in entity.vertices:
                try:
                    loc = v.dxf.location
                    coords.append((loc.x, loc.y))
                except AttributeError:
                    pass
        return coords
    
    def update_scaling(self):
        # Update scale factors
        self.panel_scaler.scale_factors['width'] = self.width_spin.value() / 400
        self.panel_scaler.scale_factors['height'] = self.height_spin.value() / 600
        self.panel_scaler.scale_factors['depth'] = self.depth_spin.value() / 200
        
        # Update plot
        self.update_plot()
    
    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Plot scaled panels
        panel_colors = {
            'LEFTRIGHT': 'black',
            'FRONTBACK': 'purple',
            'BOTTOM': 'teal'
        }
        
        current_y = 0
        spacing = 20  # mm spacing between panels
        
        for panel_name, panel_data in self.panels.items():
            # Scale panel
            scaled_data = self.panel_scaler.scale_panel(panel_name, panel_data)
            
            # Plot outline
            xs, ys = zip(*scaled_data['outline'])
            ax.plot(xs, [y + current_y for y in ys], 
                   color=panel_colors[panel_name], 
                   label=panel_name)
            
            # Plot slots
            for slot in scaled_data['slots']:
                xs, ys = zip(*slot)
                ax.plot(xs, [y + current_y for y in ys], 
                       color='blue', 
                       linestyle='-')
            
            # Plot cutlines
            for cutline in scaled_data['cutlines']:
                xs, ys = zip(*cutline)
                ax.plot(xs, [y + current_y for y in ys], 
                       color='red', 
                       linestyle='--')
            
            # Add dimensions label
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            ax.text(min(xs) + width/2, 
                   current_y + height/2,
                   f"{panel_name}\n{width:.0f}x{height:.0f}mm",
                   ha='center', va='center',
                   color=panel_colors[panel_name])
            
            # Update Y position for next panel
            current_y += height + spacing
        
        ax.set_aspect('equal')
        ax.grid(True, linestyle=':', linewidth=0.5)
        ax.set_title('Scaled Box Panels and Cutlines')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        
        # Format axis ticks
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        
        # Move legend outside
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        self.figure.tight_layout(rect=[0, 0, 0.8, 1])
        
        # Update canvas
        self.canvas.draw()
    
    def export_dxf(self):
        # TODO: Implement DXF export
        pass

def main():
    app = QApplication(sys.argv)
    window = DXFViewer()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 