# CAPWizard for IAEA MESSAGE

## Overview
CAPWizard for IAEA MESSAGE is a sophisticated tool developed to address specific calculation complexities in the IAEA MESSAGE tool. This tool is instrumental in generating calculation applications that overcome challenges related to total installed capacity and fixed costs, particularly when plant lifespans don't align with the study years of the application. CAPWizard automates the creation of Tech and LDR CAP files, facilitating the processing of results into formats that enrich the data beyond what is available in standard MESSAGE outputs. This enriched data allows for advanced analysis and visualization in MS Excel, including the use of pivot tables with extensive filtering options.

A distinctive feature of CAPWizard is its support for LDR results processing, which can be challenging without such a tool. The application is further enhanced by a customizable template Excel file, enabling users to tailor the tool to their specific model requirements. For instance, users can add generation types to technologies in the model, allowing for more detailed filtering in the processed results.


## Requirements
- Windows OS or macOS to run the packaged application.


## Installation

For end-users:

- For macOS: Download and install the provided `.dmg` file. Additionally, download the `template.xlsx` to customize the tool for your specific model.
- For Windows: Use the provided installer and download the `template.xlsx` for model customization.

For developers and advanced users:

- The source code is open-sourced for those who wish to tailor or extend the application.
- Python environment setup and dependencies are documented for development purposes.


## Usage

1. **Select ADB File**: Browse and select the desired ADB file for CAP file generation or result processing.
2. **Set Parameters**: Input required parameters such as the number of runs for simulations.
3. **Generate CAP Files**: Use the 'Generate Tech CAP' or 'Generate LDR CAP' buttons to create capacity files, which are then used in MESSAGE.
4. **Process Simulation Outputs**: Import MESSAGE simulation results into Excel, fill in the template file, and use CAPWizard to process these results for detailed analysis.


## Packaging for Developers

- Use `package_app.py` to package your modified version of the application.
- On macOS, ensure `create_dmg` is installed for `.dmg` file creation.


## Contributing
Contributions, issues, and feature requests are welcome. Feel free to check the issues page for contributing.


## License
This software is released under the Apache License 2.0. This license is a permissive open-source license that includes provisions for attribution. It allows users to use, modify, and distribute the software while requiring proper credit to be given to the original author. Therefore, any redistribution of this software must clearly attribute development to the author, Yousef S. Al-Qattan from Kuwait Institute for Scientific Research (KISR). 

## Author

Developed by Yousef S. Al-Qattan, Kuwait Institute for Scientific Research (KISR).


## Acknowledgements

Special thanks to Dr. Emmanuel Guemene Dountio and Dr. Arvydas Gallinis for their guidance and support throughout the development of this tool.

