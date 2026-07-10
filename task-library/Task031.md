# Task031: check-attribute-mandatory

**Goal**: 验证所有必填属性（IFC schema WHERE rules）

**Input**: Any IFC file
**Output**: Report listing missing mandatory attributes
**Constraint**: All mandatory schema attributes must be populated
**Affected Classes**: All entities
**Difficulty**: 1/5
**Frequency**: High
**Business Value**: 10/10
**Source**: buildingSMART validation: schema compliance; normative checks

## Description

*Real-world task derived from buildingSMART validation: schema compliance; normative checks. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
