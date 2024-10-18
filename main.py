import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt  # Import Qt for alignment constants

# Add gmid to the path for module imports
sys.path.append(os.path.abspath("gmid"))

import re

from mosplot import load_lookup_table, LoadMosfet
import matplotlib.pyplot as plt
import lookup_tables  # Import the external functionality for Lookup Tables

class OADTMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OADT - Open Analog Design Toolbox")
        self.setGeometry(100, 100, 600, 600)
        self.setFixedSize(600, 500)  # Set fixed size to maintain the box shape

        # Set up the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add each tab (Look-up Tables, GMID Curves, Design Tool)
        self.tabs.addTab(self.create_lookup_tab(), "Look-up Tables")
        self.tabs.addTab(self.create_gmid_tab(), "gm/ID Curves")
        

    # Create tab for Look-up Tables
    def create_lookup_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Input fields for generating the lookup table
        # Add Plot Type Dropdown
        self.simulator_input = QComboBox()
        self.simulator_input.addItems([
            "ngspice",
            "hspice"
        ])
        
        self.model_paths_input = QLineEdit()
        self.raw_spice = QLineEdit()
        self.nmos_model_name = QLineEdit()
        self.pmos_model_name = QLineEdit()
        self.vsb_input = QLineEdit()
        self.vgs_input = QLineEdit()
        self.vds_input = QLineEdit()
        self.width_input = QLineEdit()
        self.lengths_input = QLineEdit()
        self.lut_name_input = QLineEdit()

        # Set fixed width for input fields
        input_width = 300
        #form_layout.addRow("Simulator:", self.simulator_input)
        self.model_paths_input.setFixedWidth(input_width)
        self.raw_spice.setFixedWidth(input_width)
        self.nmos_model_name.setFixedWidth(input_width)
        self.pmos_model_name.setFixedWidth(input_width)
        self.vsb_input.setFixedWidth(input_width)
        self.vgs_input.setFixedWidth(input_width)
        self.vds_input.setFixedWidth(input_width)
        self.width_input.setFixedWidth(input_width)
        self.lengths_input.setFixedWidth(input_width)
        self.lut_name_input.setFixedWidth(input_width)

        form_layout.addRow("Simulator:", self.simulator_input)
        form_layout.addRow("Model Paths:", self.model_paths_input)

        # Add button next to Model Paths
        self.model_path_button = QPushButton("Select Model Files")
        self.model_path_button.clicked.connect(self.select_model_files)
        # Create a layout for the button to place it next to the input
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.model_path_button)
        form_layout.addRow("", button_layout)  # Add empty label to maintain alignment

        form_layout.addRow("Raw Spice (Optional):", self.raw_spice)
        form_layout.addRow("NMOS Model Name:", self.nmos_model_name)
        form_layout.addRow("PMOS Model Name:", self.pmos_model_name)
        form_layout.addRow("VSB (start, stop, step):", self.vsb_input)
        form_layout.addRow("VGS (start, stop, step):", self.vgs_input)
        form_layout.addRow("VDS (start, stop, step):", self.vds_input)
        form_layout.addRow("Width:", self.width_input)
        form_layout.addRow("Lengths (comma-separated):", self.lengths_input)
        form_layout.addRow("LUT Name (without extension):", self.lut_name_input)

        generate_button = QPushButton("Generate Lookup Table")
        generate_button.setFixedWidth(200)  # Set fixed width for the button
        generate_button.clicked.connect(self.generate_lookup_table)

        # Add a small space between the LUT name input and the generate button
        form_layout.addRow("", QLabel())  # Add an empty label for spacing
        form_layout.addRow("", generate_button)  # Add generate button without a label

        layout.addLayout(form_layout)
        layout.setStretch(0, 1)  # Stretch the form layout
        tab.setLayout(layout)
        return tab

    def select_model_files(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Model Files", "", "All Files (*);;Text Files (*.txt)", options=options)
        # Get the directory where main.py is located
        main_dir = os.path.dirname(os.path.abspath(__file__))
        # Convert to relative paths
        file_paths = [os.path.relpath(path, main_dir) for path in file_paths]
        
        if file_paths:
            self.model_paths_input.setText(", ".join(file_paths))  # Set the selected paths

    def generate_lookup_table(self):
        simulator = self.simulator_input.currentText()
        model_paths = self.model_paths_input.text().split(",")  # Split by comma
        raw_spice = self.raw_spice.text()
        model_names = { "nmos":self.nmos_model_name.text(), "pmos":self.pmos_model_name.text()}
        vsb = tuple(map(float, self.vsb_input.text().split(",")))  # Convert to tuple
        vgs = tuple(map(float, self.vgs_input.text().split(",")))
        vds = tuple(map(float, self.vds_input.text().split(",")))
        width = float(self.width_input.text())
        lengths = list(map(float, self.lengths_input.text().split(",")))
        lut_name = self.lut_name_input.text() + ".npy"  # Add extension to LUT name

        # Create LUT directory if it doesn't exist
        lut_dir = os.path.join(os.getcwd(), "GeneratedLUTs")
        os.makedirs(lut_dir, exist_ok=True)  # Create directory if it doesn't exist

        # Call the function to generate the lookup table
        lookup_table_file = os.path.join(lut_dir, lut_name)
        lookup_tables.generate_lookup_table(simulator, model_paths, raw_spice, model_names, vsb, vgs, vds, width, lengths, lookup_table_file)

        # Show success message
        QMessageBox.information(self, "Success", f"Lookup table generated at:\n{lookup_table_file}", QMessageBox.Ok)



    def create_gmid_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Input fields for GMID Curves
        self.lookup_table_input = QLineEdit()
        self.mos_type_input = QLineEdit()  # NMOS or PMOS
        self.vsb_input_gmid = QLineEdit()
        self.vds_input_gmid = QLineEdit()
        self.vgs_input_gmid = QLineEdit()
        self.lengths_input_gmid = QLineEdit()

        # Add buttons and input fields to the form layout
        form_layout.addRow("Lookup Table Path:", self.lookup_table_input)

        # Button to load the lookup table
        load_button = QPushButton("Load Lookup Table")
        load_button.clicked.connect(self.load_lookup_table_dialog)
        form_layout.addRow(load_button)

        form_layout.addRow("MOS Type (nmos/pmos):", self.mos_type_input)
        form_layout.addRow("VSB (Bulk-Source Voltage):", self.vsb_input_gmid)
        form_layout.addRow("VDS (Drain-Source Voltage):", self.vds_input_gmid)
        form_layout.addRow("VGS Range (Gate-Source Voltage):", self.vgs_input_gmid)
        form_layout.addRow("Lengths (comma-seperated)", self.lengths_input_gmid)
     
        # Add Plot Type Dropdown
        self.plot_type_dropdown = QComboBox()
        self.plot_type_dropdown.addItems([
            "Current Density (ID/W)", 
            "Gain Plot (gm/gds)", 
            "Transit Frequency (ft)", 
            "Early Voltage (VA)",
            "Custom Expression"
        ])
        form_layout.addRow("Y-Expression(x=gm/ID):", self.plot_type_dropdown)

        # Custom Expression QLineEdit
        self.custom_expression_input = QLineEdit()
        self.custom_expression_input.setPlaceholderText("Enter custom expression")
        self.custom_expression_input.hide()  # Initially hidden
        form_layout.addRow("Custom Expression:", self.custom_expression_input)

        # Connect the combo box signal to show/hide the custom expression input
        self.plot_type_dropdown.currentIndexChanged.connect(self.toggle_custom_expression)

        

        # Button to generate the plot
        generate_gmid_button = QPushButton("Generate gm/ID Curve")
        generate_gmid_button.clicked.connect(self.generate_gmid_curve)
        form_layout.addRow(generate_gmid_button)

        #Custom Graph Entry
        self.custom_x_expression_input = QLineEdit()
        self.custom_y_expression_input = QLineEdit()

        form_layout.addRow("X Custom Expression:", self.custom_x_expression_input)
        form_layout.addRow("Y Custom Expression:", self.custom_y_expression_input)

        # Button to generate the plot
        generate_custom_button = QPushButton("Generate Custom Curve")
        generate_custom_button.clicked.connect(self.generate_custom_curve)
        form_layout.addRow(generate_custom_button)


        layout.addLayout(form_layout)
        tab.setLayout(layout)
        return tab

    def load_lookup_table_dialog(self):
        # Use QFileDialog to get the lookup table file path
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Lookup Table File", "", "Numpy Files (*.npy)", options=options)
        if file_path:
            self.lookup_table_input.setText(file_path)

    def generate_gmid_curve(self):
        # Get inputs from the GUI fields
        lookup_table_path = self.lookup_table_input.text()
        mos_type = self.mos_type_input.text().lower()  # 'nmos' or 'pmos'
        vsb = float(self.vsb_input_gmid.text())
        vds = float(self.vds_input_gmid.text())
        vgs = tuple(map(float, filter(lambda x: x.replace('.', '', 1).isdigit(), self.vgs_input_gmid.text().split(','))))
        lengths = []
        if len(self.lengths_input_gmid.text()) != 0 :
            lengths = list(map(float, self.lengths_input_gmid.text().split(","))) 

        if(mos_type == "pmos"):
            vsb = -vsb
            vds = -vds
            vgs = vgs[::-1]
            vgs = (-1 * vgs[0], -1 * vgs[1])

        try:
            # Load the lookup table
            lookup_table = load_lookup_table(lookup_table_path)

            # Create the MOSFET object
            mosfet = LoadMosfet(lookup_table=lookup_table, mos=mos_type, vsb=vsb, vds=vds,vgs=vgs)

            # Get selected plot type
            plot_type = self.plot_type_dropdown.currentText()

            # Generate the selected plot
            if(len(lengths) == 0):
                if plot_type == "Current Density (ID/W)":
                    mosfet.current_density_plot()
                elif plot_type == "Gain Plot (gm/gds)":
                    mosfet.gain_plot()
                elif plot_type == "Transit Frequency (ft)":
                    mosfet.transit_frequency_plot()
                elif plot_type == "Early Voltage (VA)":
                    mosfet.early_voltage_plot()
                else:
                    # For custom expression
                    lambda_expression, found_vars = self.convert_to_lambda(self.custom_expression_input.text())
                    mosfet.plot_by_expression(
                        x_expression = mosfet.gmid_expression,
                        y_expression = {
                           "variables": found_vars,
                           "function": lambda_expression,
                           "label": self.custom_expression_input.text() 
                        },
                    )
            
            else:
                if plot_type == "Current Density (ID/W)":
                    mosfet.current_density_plot(lengths=lengths)
                elif plot_type == "Gain Plot (gm/gds)":
                    mosfet.gain_plot(lengths=lengths)
                elif plot_type == "Transit Frequency (ft)":
                    mosfet.transit_frequency_plot(lengths=lengths)
                elif plot_type == "Early Voltage (VA)":
                    mosfet.early_voltage_plot(lengths=lengths)
                else:
                    # For custom expression
                    lambda_expression, found_vars = self.convert_to_lambda(self.custom_expression_input.text())
                    mosfet.plot_by_expression(
                        x_expression = mosfet.gmid_expression,
                        y_expression = {
                           "variables": found_vars,
                           "function": lambda_expression,
                           "label": self.custom_expression_input.text() 
                        },
                        lengths=lengths
                    )

            # Show the plot using matplotlib
            plt.show()

        except Exception as e:
            print(f"An error occurred: {e}")
    
    def convert_to_lambda(self,expr):
         # Convert all variables to lowercase
        expr = expr.lower()
        var_mapping = ["gm", "vth", "vdsat", "vgs", "id", "gmbs", "gds", "cgg", "cgs", "cbg","cgd", "cdd"]
        # Find all unique variables in the expression that match the var_mapping
        found_vars = []
        for var in var_mapping:
            if re.search(r'\b' + var.lower() + r'\b', expr):
                found_vars.append(var.lower())  # Store the actual variable found

        # Replace each found variable with the corresponding lambda variable (x, y, z, etc.)
        for i, var in enumerate(found_vars):
            expr = re.sub(r'\b' + var + r'\b', f'{chr(120 + i)}', expr)  # chr(120) = 'x'

        # Create lambda argument list (x, y, z, ...)
        lambda_args = ', '.join([f'{chr(120 + i)}' for i in range(len(found_vars))])

        # Create the lambda function as a string
        lambda_expr = f'lambda {lambda_args} : {expr}'

        # Evaluate the string to a real lambda function
        return eval(lambda_expr), found_vars

    def toggle_custom_expression(self):
        """Show or hide the custom expression text box based on the selected plot type."""
        if self.plot_type_dropdown.currentText() == "Custom Expression":
            self.custom_expression_input.show()
        else:
            self.custom_expression_input.hide()

    def generate_custom_curve(self):

         # Get inputs from the GUI fields
        lookup_table_path = self.lookup_table_input.text()
        mos_type = self.mos_type_input.text().lower()  # 'nmos' or 'pmos'
        vsb = float(self.vsb_input_gmid.text())
        vds = float(self.vds_input_gmid.text())
        vgs = tuple(map(float, filter(lambda x: x.replace('.', '', 1).isdigit(), self.vgs_input_gmid.text().split(','))))
        lengths = []
        if len(self.lengths_input_gmid.text()) != 0 :
            lengths = list(map(float, self.lengths_input_gmid.text().split(","))) 

        if(mos_type == "pmos"):
            vsb = -vsb
            vds = -vds
            vgs = vgs[::-1]
            vgs = (-1 * vgs[0], -1 * vgs[1])

        try:
            # Load the lookup table
            lookup_table = load_lookup_table(lookup_table_path)

            # Create the MOSFET object
            mosfet = LoadMosfet(lookup_table=lookup_table, mos=mos_type, vsb=vsb, vds=vds,vgs=vgs)

            # Get selected plot type
            plot_type = self.plot_type_dropdown.currentText()

            x_expr ,found_x_vars = self.convert_to_lambda(self.custom_x_expression_input.text())
            y_expr ,found_y_vars = self.convert_to_lambda(self.custom_y_expression_input.text())

            if(len(lengths) == 0):
                mosfet.plot_by_expression(
                    x_expression = {
                        "variables": found_x_vars,
                        "function" : x_expr,
                        "label": self.custom_x_expression_input.text()
                    },
                    y_expression= {
                        "variables": found_y_vars,
                        "function": y_expr,
                        "label": self.custom_y_expression_input.text()
                    }
                )
            else:
                mosfet.plot_by_expression(
                    x_expression = {
                        "variables": found_x_vars,
                        "function" : x_expr,
                        "label": self.custom_x_expression_input.text()
                    },
                    y_expression= {
                        "variables": found_y_vars,
                        "function": y_expr,
                        "label": self.custom_y_expression_input.text()
                    },
                    lengths=lengths
                )
            
            # Show the plot using matplotlib
            plt.show()

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OADTMainWindow()
    window.show()
    sys.exit(app.exec_())
