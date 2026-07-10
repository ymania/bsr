# Task035: check-ifc-object-names

**Goal**: 验证所有 IfcBuildingElement 有名称

**Input**: IFC with unnamed elements
**Output**: Report listing unnamed elements
**Constraint**: Each element should have descriptive name
**Affected Classes**: All IfcBuildingElement
**Difficulty**: 1/5
**Frequency**: High
**Business Value**: 8/10
**Source**: buildingSMART common practice checks; BIMTester

## Description

*Real-world task derived from buildingSMART common practice checks; BIMTester. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
