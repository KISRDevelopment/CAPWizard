# Changelog for CAPWizard for IAEA MESSAGE

All notable changes to this project will be documented in this file.

### [v20240518] - 2024-05-18
- Fix issue in LDR cin file equation generator to handle special case when type is 'main input' and technology is connected to 'demand'.
- Fix issue in slice numbering in LDR.


### [v20240516] - 2024-05-16
- Include technology inputs in LDR cin file generator to be processed.


### [v20240314] - 2024-03-14
- Include demand level in LDR cin file generator to be processed.
- Implement check for update. When there is an update, the version label turns red and become clickable.
- Fix bug in progress when processing LDR only.


### [v20240313] - 2024-03-13
- Add MESSAGE demo case as a reference based on MESSAGE Demo_Case5.
- Fix issue in Tech CAP generation when all PLL are c (constants).
- Fix issue in LDR CAP generation when there is more than one day type.
- Fix bug that caused the application to crash when interpolation run option is selected


### [v20240307] - 2024-03-07
- Fix issue for import and export tech_activity in LDR sheets.
- Fixed 'Units' column in LDR sheets.


### [v20240129] - 2024-01-29
- Cost Calculation feature: Introduce new cost calculation feature to get the variable and fixed cost for running a certain technology. The cost is calculated for each  technology as the costs to run the technology summed with the cost to run its sources.
- Units Column: Introduced a new 'Units' column to enhance data clarity and accuracy.
- Fixed Units in Tech Cap .cin File: Adjusted the units in the Tech Cap .cin file for improved consistency and correctness.


### [v20240104] - 2024-01-04
- Initial release of CAPWizard for IAEA MESSAGE.