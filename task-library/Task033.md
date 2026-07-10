# Task033: normalize-owner-history

**Goal**: 统一设置所有实体的 IfcOwnerHistory

**Input**: IFC with inconsistent owner info
**Output**: IFC with uniform owner history
**Constraint**: All entities must have populated OwnerHistory
**Affected Classes**: All entities
**Difficulty**: 2/5
**Frequency**: Low
**Business Value**: 6/10
**Source**: buildingSMART ownership compliance; implementer agreements

## Description

*Real-world task derived from buildingSMART ownership compliance; implementer agreements. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
