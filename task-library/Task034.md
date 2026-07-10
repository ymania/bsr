# Task034: check-ifc-space-names

**Goal**: 验证所有 IfcSpace 有非空唯一名称

**Input**: IFC with unnamed or duplicate spaces
**Output**: Report listing unnamed/duplicate spaces
**Constraint**: Each space must have unique non-empty name
**Affected Classes**: IfcSpace
**Difficulty**: 1/5
**Frequency**: High
**Business Value**: 9/10
**Source**: buildingSMART industry practices; IDS requirements

## Description

*Real-world task derived from buildingSMART industry practices; IDS requirements. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
