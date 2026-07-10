# Task030: check-spatial-containment

**Goal**: 验证所有 IfcBuildingElement 有且仅有一个空间容器

**Input**: IFC with elements missing spatial containment
**Output**: Report listing orphan elements
**Constraint**: Each element must be in exactly one IfcBuildingStorey
**Affected Classes**: IfcBuildingElement, IfcRelContainedInSpatialStructure
**Difficulty**: 2/5
**Frequency**: High
**Business Value**: 10/10
**Source**: buildingSMART SPS007; validation service gherkin rules

## Description

*Real-world task derived from buildingSMART SPS007; validation service gherkin rules. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
