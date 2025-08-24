# Minimalism Standards for AI Agents

**Purpose**: Mandatory development principles for all AI agents working on CNG-RTK-HUB project.  
**Enforcement**: These rules must be followed for all code, documentation, and architecture decisions.

---

## 🎯 **Core Principles**

### **1. Minimal Viable Everything**
- **Documentation**: Only document what's essential for implementation
- **Code**: Write the simplest solution that works
- **Features**: Implement only current phase requirements
- **Architecture**: Design for today's needs, not tomorrow's possibilities

### **2. Single Source of Truth**
- **No Duplication**: Each concept documented/implemented in exactly one place
- **Cross-Reference**: Link to existing content instead of copying
- **Consolidation**: Merge overlapping functionality rather than parallel development
- **Validation**: Before adding anything, verify it doesn't exist elsewhere

### **3. Progressive Disclosure**
- **Start Simple**: Begin with minimal implementation
- **Add Incrementally**: Enhance only when requirements prove necessary
- **Defer Complexity**: Advanced features belong in future phases
- **Evidence-Based**: Require concrete need before adding complexity

---

## 📏 **Size Limits (MANDATORY)**

### **Documentation Files**
- **Maximum per file**: 150 lines
- **Average target**: 100 lines
- **Code examples**: Pseudocode only, no full implementations
- **Cross-references**: Use links instead of duplicating content

### **Code Files**
- **Classes**: Maximum 200 lines
- **Functions**: Maximum 50 lines
- **Modules**: Single responsibility principle
- **Comments**: Explain why, not what

### **Implementation Phases**
- **Milestones**: Maximum 4 per major phase
- **Checkpoints**: Maximum 3 per milestone
- **Features**: One primary goal per checkpoint
- **Dependencies**: Minimize inter-checkpoint dependencies

---

## 🚫 **Prohibited Practices**

### **Documentation Anti-Patterns**
- **Future Feature Planning**: No specifications for post-MVP features
- **Implementation Details**: No code examples in architecture docs
- **Duplicate Explanations**: Reference existing content instead
- **Over-Specification**: Avoid premature optimization documentation

### **Code Anti-Patterns**
- **Premature Optimization**: Don't optimize until bottlenecks are proven
- **Feature Creep**: Stick to defined milestone scope
- **Copy-Paste Development**: Extract reusable components instead
- **Over-Engineering**: Avoid complex solutions for simple problems

### **Architecture Anti-Patterns**
- **Gold Plating**: Don't add features not in requirements
- **Architecture Astronauts**: Focus on practical implementation
- **Framework Bloat**: Use minimal dependencies
- **Analysis Paralysis**: Prefer working code over perfect design

---

## ✅ **Required Practices**

### **Before Adding Anything**
1. **Verify Necessity**: Is this required for current milestone?
2. **Check Existence**: Does this already exist elsewhere?
3. **Size Validation**: Will this exceed size limits?
4. **Simplicity Test**: Is this the simplest possible solution?

### **Documentation Workflow**
1. **Single File Check**: Can this fit in existing file?
2. **Reference Strategy**: Link to existing content instead of duplicating
3. **Implementation Focus**: Document for immediate development needs
4. **Size Monitoring**: Track line counts against limits

### **Code Workflow**
1. **Minimal Implementation**: Start with simplest working solution
2. **Refactor for Reuse**: Extract common patterns into shared components
3. **Test-Driven**: Write tests that prove minimal requirements
4. **Incremental Enhancement**: Add features only when needed

---

## 📊 **Compliance Monitoring**

### **Documentation Metrics**
- **Total line count**: Must not exceed 500 lines across all active docs
- **File count**: Maximum 5 active documentation files
- **Redundancy check**: Zero duplicate concepts across files
- **Cross-reference ratio**: 80% of related content should use references

### **Code Metrics**
- **Cyclomatic complexity**: Maximum 10 per function
- **Code reuse**: Minimum 70% of functionality should use shared components
- **Test coverage**: Minimum 80% for implemented features
- **Dependency count**: Minimize external dependencies

### **Implementation Metrics**
- **Milestone scope**: Maximum 1 week per milestone
- **Feature completion**: 100% of milestone features before adding new ones
- **Technical debt**: Address immediately, don't accumulate
- **Performance**: Meet targets with minimal resource usage

---

## 🎯 **Agent-Specific Guidelines**

### **Analyzer - Discuss**
- **Analysis scope**: Focus on immediate implementation needs
- **Recommendations**: Maximum 3 actionable items
- **Complexity assessment**: Bias toward simplicity
- **Documentation**: Prefer existing content over new analysis

### **Refactor - Analyse**
- **Dependency mapping**: Include only direct dependencies
- **Change proposals**: Minimal, focused modifications
- **Risk assessment**: Consider only immediate risks
- **Branch planning**: Maximum 3 checkpoints per branch

### **Refactor - Implement**
- **Implementation scope**: Stick strictly to defined checkpoints
- **Code style**: Prioritize readability over cleverness
- **Testing strategy**: Focus on essential functionality
- **Commit granularity**: Small, focused commits

---

## 🔄 **Enforcement Mechanism**

### **Pre-Implementation Checklist**
- [ ] Requirement exists in current milestone
- [ ] No existing solution for this problem
- [ ] Proposed solution is minimal and simple
- [ ] Size limits will not be exceeded
- [ ] Cross-references used instead of duplication

### **Review Criteria**
- **Necessity**: Does this solve a proven problem?
- **Simplicity**: Is this the simplest possible solution?
- **Reusability**: Can this be shared with other components?
- **Maintainability**: Will this be easy to modify later?

### **Violation Response**
1. **Immediate refactoring** to comply with standards
2. **Documentation of reasoning** for any exceptions
3. **Size reduction** to meet established limits
4. **Consolidation** of duplicate functionality

---

## 📖 **Examples**

### **Good Practice: Minimal Documentation**
```markdown
## Driver Interface
- Connect to receiver
- Parse protocol data
- Return normalized state
See: protocol-mappings.md for details
```

### **Bad Practice: Over-Specification**
```markdown
## Driver Interface Implementation Strategy
The driver interface provides a standardized contract...
[200 lines of detailed implementation code examples]
```

### **Good Practice: Simple Code**
```python
def parse_ubx(data: bytes) -> GNSSState:
    return normalize_ubx_nav_pvt(data)
```

### **Bad Practice: Over-Engineering**
```python
class UBXParserFactory:
    # 50 lines of factory pattern implementation
    # for a simple parsing function
```

---

**Enforcement Date**: August 24, 2025  
**Review Cycle**: Every milestone completion  
**Compliance**: Mandatory for all AI agents
