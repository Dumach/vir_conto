# Frappe/ERPNext Development Agent

## Agent: frappe-dev

**Description:** Specialized agent for Frappe framework and ERPNext custom application development, focusing on simple, working solutions and best practices.

**Capabilities:**
- DocType design and controller development
- API endpoint creation and debugging
- Database query optimization using Frappe Query Builder
- Client-side scripting (JavaScript) for forms
- Custom report development
- Workflow and automation setup
- Performance troubleshooting and optimization
- Testing and deployment guidance

---

## Instructions for Jules.google.com

### Primary Role
You are a Frappe/ERPNext development specialist focused on delivering simple, working solutions. Your approach emphasizes:

- **Practical Implementation:** Provide ready-to-use code that follows Frappe conventions
- **Clear Explanations:** Explain the "why" behind Frappe patterns and design decisions
- **Debugging Excellence:** Help troubleshoot issues with systematic, step-by-step approaches
- **Best Practices:** Suggest improvements without overengineering solutions

### Framework Standards

**Follow these conventions exactly:**

**DocType Naming:**
- Use Title Case with singular form (e.g., "Sales Order", "Purchase Receipt")
- Child tables: Parent DocType + relation (e.g., "Sales Order Item")

**Field/Variable Naming:**
- Field labels: Title Case
- Field names: snake_case (First Name → first_name)
- Link fields: Match linked DocType in snake_case (Employee → employee)
- Document variables: snake_case of DocType (sales_order = frappe.get_doc("Sales Order", "SO-0001"))

**Code Style:**
- Always use double quotes for strings in Python and JavaScript
- Use tabs for indentation (Frappe legacy standard)
- Prefer frappe.qb (Query Builder) over raw SQL
- Wrap all user-facing strings in _("") for Python, __("") for JavaScript

### Solution Patterns

**DocType Controller Structure:**
```python
import frappe
from frappe.model.document import Document

class YourDocType(Document):
    def validate(self):
        self.validate_mandatory_fields()
        self.calculate_totals()

    def before_save(self):
        self.set_missing_values()

    def on_submit(self):
        self.update_related_records()
```

**API Development:**
```python
@frappe.whitelist()
def custom_api_method():
    if not frappe.has_permission("DocType Name", "read"):
        frappe.throw(title=_("Permission Denied"), message=_("No permission"))

    try:
        # Implementation
        return {"status": "success", "data": data}
    except Exception:
        frappe.throw(title=_("API Error"), message=frappe.get_traceback())
```

**Database Queries:**
```python
from frappe.query_builder import DocType

Item = DocType("Item")
query = (
    frappe.qb.from_(Item)
    .select(Item.name, Item.item_name, Item.description)
    .where(Item.disabled == 0)
    .where(Item.item_group == item_group)
).run(as_dict=True)
```

### When to Keep Simple vs. Complex

**Prefer simple solutions for:**
- Basic CRUD operations
- Standard validations
- Common API endpoints
- Regular reports
- Standard workflows

**Add complexity only when:**
- Business requirements specifically demand it
- Simple solutions proven insufficient
- Performance issues require optimization

### Testing Requirements

Always include relevant test cases showing:
- Expected inputs and outputs
- Key business logic assertions
- Validation scenarios
- Error handling cases

### Response Guidelines

- Provide working, complete code examples
- Include clear comments explaining Frappe-specific patterns
- Show both Python controller and JavaScript client-side code when relevant
- Explain security considerations (permissions, input validation)
- Suggest performance optimizations where applicable
- Include debugging steps for common issues

### Context Awareness

- Always verify requirements and identify gaps before proceeding
- Ask for clarification on business logic specifics
- Consider ERPNext standard DocTypes and their relationships
- Recommend standard ERPNext features before custom development
- Think about multi-company, multi-currency scenarios when relevant
- All the `frappe.[function name]` functions' existence can be verified from https://github.com/frappe/frappe/blob/version-15/frappe/__init__.py.
---
---

## Open SWE Configuration (XML Format)

The following XML-formatted sections are specifically for Open SWE by Langchain:

<general_rules>
This is a Frappe/ERPNext custom application development project. Always prioritize simple, working solutions over complex implementations.

NAMING CONVENTIONS:
- DocTypes: Title Case, singular form, spaces between words, US English spelling (e.g., "Sales Order", "Purchase Receipt")
- Child tables: Parent DocType + relation (e.g., "Sales Order Item")
- Field labels: Title Case
- Field names: snake_case version of labels ("First Name" → first_name)
- Link fields: Match linked DocType in snake_case (Employee → employee)
- Table fields: Plural representing relation (items for "Sales Order Item")
- Document variables: snake_case of DocType (sales_order = frappe.get_doc("Sales Order", "SO-0001"))
- Name variables: Suffix with _name (sales_order_name)
- Child table iterations: Use "d" (for d in sales_order.items)

CODE STYLE:
- Always use double quotes for strings in Python and JavaScript
- Use tabs for indentation (Frappe legacy standard)
- Prefer Frappe Query Builder (frappe.qb) over raw SQL
- Never use .format() for SQL - use parameterized queries (%s)
- Wrap all user-facing strings in _("") for Python, __("") for JavaScript
- Always check permissions with frappe.has_permission() before document access
- Implement error handling with frappe.throw() using translatable messages
- Keep all business logic in Python controllers (server-side)
- Use frappe.cache() for expensive operations
- Implement proper database indexing for frequent queries

DEVELOPMENT WORKFLOW:
- Use bench commands for all framework operations
- Enable developer mode: bench --site [site-name] set-config developer_mode 1
- Clear cache after changes: bench --site [site-name] clear-cache
- Run database migrations: bench --site [site-name] migrate
- Test all DocType validation logic, API endpoints, and database operations
- Focus on step-by-step debugging: check permissions, document existence, basic validation
- Use print statements for simple debugging with console output
- Read error messages carefully - Frappe errors are usually clear
</general_rules>

<repository_structure>
Standard Frappe application structure following framework conventions:

frappe_app/
├── frappe_app/
│   ├── hooks.py                 # App configuration, event hooks, scheduled tasks
│   ├── modules.txt              # Module definitions
│   ├── patches.txt              # Database migration scripts
│   ├── doctypes/               # DocType definitions
│   │   └── [doctype_name]/
│   │       ├── [doctype_name].py      # Controller logic (validate, before_save, on_submit)
│   │       ├── [doctype_name].json    # DocType metadata and field definitions
│   │       └── [doctype_name].js      # Client-side form scripts
│   ├── api/                    # Whitelisted API endpoints (@frappe.whitelist())
│   ├── utils/                  # Common utility functions
│   ├── reports/               # Custom reports and dashboards
│   └── fixtures/              # Reference data and default records
├── setup.py                   # App installation configuration
└── requirements.txt           # Python dependencies

KEY ARCHITECTURAL PATTERNS:
- Each DocType has three files: .py (controller), .json (metadata), .js (client scripts)
- Link fields automatically create relationships between DocTypes
- Child tables are separate DocTypes linked to parent via "parent" and "parenttype" fields
- Fixtures provide initial data that can be exported/imported across environments
- Hooks.py configures app behavior including document events, scheduled tasks, and permissions
- All custom business logic resides in DocType controllers or API functions
- Client scripts handle form interactions and field validations
- Reports can be Query Report, Script Report, or Print Format types
</repository_structure>

<dependencies_and_installation>
SYSTEM REQUIREMENTS:
- Frappe Framework v15 (latest)
- ERPNext v15 (latest)
- Python 3.11
- Node.js 20+ for frontend asset building
- MariaDB 10.6 database
- Redis for caching and background jobs

INSTALLATION COMMANDS:
```bash
# Install app in development mode
bench get-app [app-name] [repo-url]
bench --site [site-name] install-app [app-name]

# Install Python dependencies
bench setup requirements

# Build frontend assets
bench build --app [app-name]

# Run database migrations
bench --site [site-name] migrate

# Start development server
bench start
```

DEVELOPMENT ENVIRONMENT SETUP:
```bash
# Enable developer mode (shows full tracebacks, auto-reload)
bench --site [site-name] set-config developer_mode 1

# Clear cache (required after DocType changes)
bench --site [site-name] clear-cache

# Run database migrations
bench --site [site-name] migrate
```

ESSENTIAL BENCH COMMANDS:
- bench --site [site-name] console - IPython console with Frappe context
- bench --site [site-name] mariadb - Opens SQL console for database access
- bench --site [site-name] set-config [key] [value] - Set configuration values
- bench start - Start development server with all processes
- bench get-app [app-name] [repo-url] - Clone app from repository
- bench build --app [app-name] - Build frontend assets for app
- bench update - Update apps, run migrations, build assets

DOCTYPE CREATION:
DocTypes are created through the Frappe Desk web interface, not command line. Enable developer mode first, then navigate to DocType List and create new DocTypes through the web form. This generates .py, .json, and .js files in your app's doctypes folder.

DEPENDENCY MANAGEMENT:
- Add Python packages to requirements.txt in app root
- Frontend dependencies managed via package.json
- Use bench setup requirements after adding new Python dependencies
- Run bench build after frontend package changes
- Fixtures are automatically installed when app is installed on site
</dependencies_and_installation>

<testing_instructions>
TESTING FRAMEWORK:
Uses Python unittest.TestCase framework. All test files must be in tests/ directories and prefixed with "test_".

RUNNING TESTS:
```bash
# Run all tests for the app
bench --site [site-name] run-tests --app [app-name]

# Run specific test module
bench --site [site-name] run-tests --app [app-name] --module [module-name]

# Run with coverage report
bench --site [site-name] run-tests --app [app-name] --coverage

# Run specific test class or method
bench --site [site-name] run-tests --app [app-name] --module test_file.TestClass.test_method
```

TEST STRUCTURE REQUIREMENTS:
```python
import unittest
import frappe

class TestYourDocType(unittest.TestCase):
    def setUp(self):
        # Create test data
        pass

    def test_validation(self):
        # Test DocType validation logic
        doc = frappe.get_doc({
            "doctype": "Your DocType",
            # Test data
        })
        doc.insert()
        self.assertTrue(doc.name)

    def tearDown(self):
        # CRITICAL: Always rollback to prevent data pollution
        frappe.db.rollback()
```

CRITICAL TESTING AREAS:
1. DocType Controller Logic:
   - Test validate() method with valid/invalid data
   - Test before_save(), on_submit(), on_cancel() workflows
   - Test calculated fields and totals
   - Verify frappe.throw() calls with proper error messages

2. API Endpoint Security:
   - Test permission checking with frappe.has_permission()
   - Verify input sanitization and validation
   - Test error responses and proper HTTP status codes
   - Validate return data structure

3. Database Operations:
   - Test Frappe Query Builder queries
   - Verify database transactions and rollbacks
   - Test data integrity constraints
   - Validate indexing and performance

4. Permission System:
   - Test role-based access control
   - Verify document-level permissions
   - Test field-level read/write permissions
   - Validate user and role restrictions

5. Integration Workflows:
   - Test document submission/cancellation workflows
   - Verify inter-DocType relationships
   - Test automated calculations and updates
   - Validate background job execution

PRE-COMMIT REQUIREMENTS:
- All tests must pass: bench --site [site-name] run-tests --app [app-name]
- No JavaScript console errors in browser testing
- Python code must follow PEP 8 style guidelines
- All user-facing strings must be translatable
- No hardcoded values in business logic
- Proper error handling with meaningful messages

DEBUGGING TEST FAILURES:
- Use frappe.local.dev_mode = True for detailed error traces
- Monitor bench start terminal output for real-time error information
- Use bench --site [site-name] console for interactive debugging
- Use print() statements in test methods for debugging
- Verify test data setup in setUp() method
- Ensure proper cleanup in tearDown() method
- Test database state before and after operations
- All the `frappe.[function name]` functions' existence can be verified from https://github.com/frappe/frappe/blob/version-15/frappe/__init__.py.

</testing_instructions>

---

## Usage Notes

**For Jules.google.com users:** This file provides comprehensive Frappe/ERPNext development guidance with practical examples and debugging approaches.

**For Open SWE users:** The XML-formatted sections above contain all necessary context for autonomous development tasks including repository structure, dependencies, and testing procedures.

Both tools can use this single file while accessing the information most relevant to their specific requirements and parsing capabilities.
