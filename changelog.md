# Changelog for CAPWizard for IAEA MESSAGE

All notable changes to this project will be documented in this file.


### [v20240605] - 2024-06-05
- Fix issue in CAP generation in cases where energy forms in MESSAGE have comments


### [v20240526] - 2024-05-26
- Added lag of one period calculation of annualized investments cost since there is a lag between installation of capacity and operation of the plant.


### [v20240525] - 2024-05-25
- Process new sheet 'Investments_annualized_cost' which calculates investments for new installation for each study year over the plant life.
- Fix a bug in LDR CAP in rare cases when fyear is set to be beyond the study period.
- Fix a bug that prevented buttons from being enabled when an error occurs.
- Show message box when process completes


### [v20240522] - 2024-05-22
- Remove empty LDR columns which were included in different sheets.
- Enhanced template excel file merging into results to dynamically include non-default columns.
- Enrich src_dst_costs, src_costs, and dst_costs sheets with template columns.


### [v20240521] - 2024-05-21
- Add sensitivity to better identify demand forms in src_dst_costs, src_costs, and dst_costs sheets.
- Increase number of digits in rounding of values in src_dst_costs, src_costs, and dst_costs sheets.
- Rename column per_unit_USD_per_MWh in src_dst_costs, src_costs, and dst_costs sheets to be USD_per_MWh.


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