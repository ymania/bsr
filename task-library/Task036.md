# Task036: check-ifc-classification

**Goal**: 验证元素是否有 IfcClassification 关联

**Input**: IFC without classification
**Output**: Report listing unclassified elements
**Constraint**: Each element should have at least one classification
**Affected Classes**: All IfcElement
**Difficulty**: 2/5
**Frequency**: High
**Business Value**: 8/10
**Source**: buildingSMART bSDD compliance; classification standards

## Description

*Real-world task derived from buildingSMART bSDD compliance; classification standards. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
