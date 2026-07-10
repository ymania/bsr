# Task045: validate-ifc-ids

**Goal**: 根据 IDS (Information Delivery Specification) 文件验证 IFC

**Input**: IFC file + IDS spec file
**Output**: Compliance report per IDS requirement
**Constraint**: All IDS requirements must pass
**Affected Classes**: As defined in IDS
**Difficulty**: 3/5
**Frequency**: High
**Business Value**: 10/10
**Source**: buildingSMART IDS; IfcTester validation; BIMTester rules

## Description

*Real-world task derived from buildingSMART IDS; IfcTester validation; BIMTester rules. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
