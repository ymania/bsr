# Task026: add-pset-door-fire-rating

**Goal**: 为所有 IfcDoor 添加 Pset_DoorCommon.FireRating

**Input**: IFC without door fire rating
**Output**: IFC with FireRating on all doors
**Constraint**: Each door in fire zone must have rating
**Affected Classes**: IfcDoor, IfcPropertySet
**Difficulty**: 2/5
**Frequency**: High
**Business Value**: 9/10
**Source**: buildingSMART Pset_DoorCommon; fire code compliance

## Description

*Real-world task derived from buildingSMART Pset_DoorCommon; fire code compliance. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
