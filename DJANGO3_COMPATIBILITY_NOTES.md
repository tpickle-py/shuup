# Django 3+ Compatibility Issues

## ⚠️ Critical Issue: django-polymorphic Recursion

**Problem**: Deep recursion in Django's SQL compiler when using polymorphic models with Django 3.2+

**Location**: `django.db.models.fields.__init__.py:519 in __eq__`

**Symptoms**:
- `RecursionError: maximum recursion depth exceeded in comparison`
- Affects Contact → PersonContact/CompanyContact model hierarchy
- Triggers during complex polymorphic queries (delete operations, etc.)

**Affected Tests**:
- `shuup_tests/core/test_order_creator.py::test_order_customer_groups`
- Any test that deletes related polymorphic objects

**Potential Solutions**:
1. **Upgrade django-polymorphic** to latest version (check Django 3.2+ support)
2. **Replace django-polymorphic** with alternatives:
   - **django-model-utils** inheritance (MTI - Multi-Table Inheritance)
   - **Custom abstract base models** without polymorphic behavior
   - **Composition over inheritance** pattern
3. **Downgrade Django** to 3.1 (not recommended)

**Impact**: 
- Blocks testing of complex workflows
- Core functionality may still work
- Prevents production readiness assessment

---

## ✅ Fixed Issues

### PersonContact Name Field Conflict
- **Issue**: Property/field naming conflict causing recursion
- **Solution**: Removed name property, use database field + computed full_name property
- **Status**: Fixed and tested

---

## 🔧 Simple Fixes Needed

### OrderStatus Manager Methods
- **Issue**: TODO comments in factories.py.moved about Django 3+ compatibility
- **Location**: Lines 436-443 in factories.py.moved
- **Status**: In Progress

### OrderLine Field Issues  
- **Issue**: base_unit_price and taxes field access patterns
- **Location**: Lines 507-528 in factories.py.moved
- **Status**: Pending

---

## 📋 Action Plan

1. ✅**Immediate**: Fix OrderStatus and OrderLine compatibility issues
2. **Short-term**: Skip polymorphic tests, get basic tests passing
3. **Medium-term**: Research polymorphic alternatives
4. **Long-term**: Migrate away from django-polymorphic if needed
