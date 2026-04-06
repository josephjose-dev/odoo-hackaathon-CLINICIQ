# Teacher's Odoo Mental Model — Extracted from 4 Workshop Sessions
# Instructor: Sha Elango, Technical Education Consultant at Odoo

===============================================================================
SESSION 1 TEACHINGS
===============================================================================

## Core Philosophy (Teacher's Own Words)
- "Python classes correspond directly to database tables in PostgreSQL — they ARE the tables"
- "Apps and modules are used interchangeably. Tables and models refer to the same thing."
- "Backend is Python. Frontend is XML. Database is PostgreSQL — but you mostly write Python and XML."
- "Full-stack parallel: Python = backend logic, XML = frontend views, same as Flask + HTML"
- Tech stack: Python + PostgreSQL + XML. JavaScript is NOT commonly used in core Odoo.

## File Structure (Teacher's Exact Mental Model)
```
module_name/
├── __init__.py          # imports models/ package
├── __manifest__.py      # metadata + load order
├── models/
│   ├── __init__.py      # imports each model file
│   └── *.py             # one file per model/table
├── views/
│   └── *.xml            # views, actions, menus
└── security/
    └── ir.model.access.csv  # CRUD permissions
```

## CRITICAL: Load Order in manifest (Teacher stressed this repeatedly)
1. security/ir.model.access.csv  ← FIRST
2. views/*_views.xml             ← views BEFORE menus
3. views/*_menus.xml             ← menus LAST (menus reference actions in views)
"Views defining actions must load before menus referencing those actions."
"If you mess up the order you get errors because menus reference things not yet defined."

## Models — Teacher's Exact Patterns

### Mandatory fields for EVERY class:
```python
class MyModel(models.Model):
    _name = "module.model"        # REQUIRED — this IS the table name
    _description = "Description"  # optional but good practice
```

Teacher: "The most important thing — _name — you MUST specify for every class you create."
Teacher: "Description is optional but if someone else reads your code they know what the table is."

### Field Types Taught:
```python
fields.Char()       # text
fields.Text()       # long text  
fields.Float()      # decimal
fields.Integer()    # whole number (used for area — "simpler for calculations")
fields.Boolean()    # true/false
fields.Selection()  # dropdown — SYNTAX: [('stored_val','Displayed Val'), ...]
fields.Date()       # date
```

### Selection Field — Key Teaching:
```python
state = fields.Selection([
    ('new', 'New'),
    ('offer_received', 'Offer Received'),
    ('sold', 'Sold'),
])
```
Teacher: "The first value is what's STORED in database (lowercase). The second is what's SHOWN 
on frontend (readable). When you do Python comparisons you use the stored value:
if record.state == 'sold'"

## Security CSV — Teacher's Exact Format:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_estate_property,access_estate_property,model_estate_property,base.group_user,1,1,1,1
```
- 1,1,1,1 = full CRUD for all internal users
- Teacher: "During your projects you can do the same thing unless you want different users 
  to have different access rights."

## Developer Mode — Teacher's Exact Steps:
Settings → Developer Tools → Activate Developer Mode
Then: Settings → Technical → Models → search your model name
"This confirms your model is registered and ready."

## Upgrading Module — Teacher's Key Debug Tool:
Apps → search module name → three dots → Upgrade
"It will tell you EXACTLY which file, which line has the error."
Teacher said this MANY times: "Always upgrade the module first before asking for help."

===============================================================================
SESSION 2 TEACHINGS
===============================================================================

## Computed Fields — Teacher's Exact Pattern:
```python
total_area = fields.Integer(compute="_compute_total_area")

@api.depends("living_area", "garden_area")
def _compute_total_area(self):
    for record in self:
        record.total_area = record.living_area + record.garden_area
```

Teacher: "api.depends means: if living_area OR garden_area changes, recompute this field."
Teacher: "Computed fields are NOT editable from the frontend — they're grayed out."
Teacher on for loop: "self refers to ALL selected records. If you select 100 records to delete,
self = those 100. The for loop processes each one individually."

## Naming Conventions — Teacher's Exact Rules:
- Many2one field: `property_type_id`  (underscore + id)
- One2many field: `offer_ids`          (underscore + ids — PLURAL)
- Many2many field: `tag_ids`           (underscore + ids — PLURAL)

Teacher: "If I'm doing many to many it would just be _ids. Because it's many to one: _id."

## Relationships — Teacher's Teaching:
```python
# Many2one (many properties → one type)
property_type_id = fields.Many2one("estate.property.type", string="Property Type")

# One2many (one property → many offers) — INVERSE of the Many2one
offer_ids = fields.One2many("estate.property.offer", "property_id")
#                                          ^table       ^inverse field name

# Many2many
tag_ids = fields.Many2many("estate.property.tag")
```

## Inbuilt Odoo Tables — Teacher's Exact Teaching:
- `res.partner` = CLIENTS / external entities (customers, contacts)
- `res.users`   = INTERNAL USERS / employees using Odoo
Teacher: "You don't need to create a table for clients. res.partner already has name, 
email, phone — everything. Just link to it directly."
Teacher: "If I'm collaborating with a professor, they'd be res.partner. 
If they work inside the company using Odoo, they'd be res.users."

## Default Values:
```python
salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user)
```
Teacher: "self.env.user means the current logged-in user. env = Odoo environment basically."
Teacher: "We set default for salesperson because when YOU add a property, YOU are the 
salesperson. But we cannot auto-assign a buyer — we don't know who will buy yet."

## XML Views — Teacher's Patterns:

### List View with decorations:
```xml
<list string="Properties"
      decoration-danger="risk_level == 'critical'"
      decoration-warning="risk_level == 'high'"
      decoration-success="state == 'done'"
      decoration-muted="state == 'cancelled'">
    <field name="name"/>
    <field name="state"/>
</list>
```
Teacher: "decoration-success = green, decoration-danger = red, decoration-muted = gray.
These are inbuilt — you cannot change the colors."

### Form View with notebook tabs:
```xml
<form>
    <header>
        <!-- buttons and statusbar go here -->
    </header>
    <sheet>
        <group>  <!-- fixes width issues — teacher mentioned this many times -->
            <!-- main fields -->
        </group>
        <notebook>
            <page string="Tab Name">
                <!-- embedded lists or related fields -->
            </page>
        </notebook>
    </sheet>
    <chatter/>  <!-- if inheriting mail.thread -->
</form>
```
Teacher: "Put notebook in its OWN group tag separate from the field groups — this fixes 
the width issue that many people faced."

### Status Bar (one line!):
```xml
<field name="state" widget="statusbar" 
       statusbar_visible="new,offer_received,sold"
       options="{'clickable': True}"/>
```
Teacher: "The statusbar is literally just one line. Most straightforward thing ever."
Teacher: "Don't add 'cancelled' to statusbar_visible — statusbar shows PROGRESSION, 
not every possible state."

### Invisible Attribute:
```xml
<button name="action_sell" string="Sell" type="object"
        invisible="state in ('sold', 'cancelled')"/>
```
Teacher: "invisible uses Python conditions — same as any Python if statement."
Teacher: "If the property is sold, no reason to show the sell button again."

### Readonly Attribute:
```xml
<field name="offer_ids" readonly="state in ('sold', 'cancelled', 'offer_accepted')"/>
```
Teacher: "read only means the user cannot add or edit — they can only see."

### Embedded list in form (One2many display):
```xml
<page string="Offers">
    <field name="offer_ids">
        <list list_editable="bottom"
              decoration-success="status == 'accepted'"
              decoration-danger="status == 'refused'">
            <field name="price"/>
            <field name="partner_id"/>
            <field name="status"/>
            <button name="action_accept" string="Accept" 
                    type="object" icon="fa-check"
                    invisible="status in ('accepted', 'refused')"/>
        </list>
    </field>
</page>
```
Teacher on list_editable="bottom": "This means you can edit the offer directly in the 
list row — you don't need to open the form. Bottom means the add button is at bottom."

## Button Pattern — Teacher's Teaching:
```xml
<button name="action_sell" string="Sell" type="object"/>
```
- `name` = exact name of the Python method
- `type="object"` = triggers a Python method (always use this for backend actions)
- `string` = label shown to user
Teacher: "The name here MUST match the Python function name exactly."

===============================================================================
SESSION 3 TEACHINGS  
===============================================================================

## Business Logic Methods — Teacher's Pattern:
```python
def action_sell(self):
    for record in self:
        if record.state == 'cancelled':
            raise UserError("Cancelled properties cannot be sold!")
        record.state = 'sold'
```
Teacher: "UserError = when the user tries to do something dumb."
Teacher: "Always loop for record in self — even if you think it's one record."

## create() Override — Teacher's Exact Teaching:
```python
@api.model
def create(self, vals):
    record = super().create(vals)
    # custom logic here
    if record.property_id:
        record.property_id.state = 'offer_received'
    return record
```
Teacher: "@api.model means this depends on the MODEL itself, not a specific field."
Teacher: "super().create() overrides Odoo's default create method. You MUST call super 
and MUST return the record."
Teacher: "This runs every time a new record is created — use it for automation."

## Sequence / Reference Numbers:
```python
name = fields.Char(default="New", copy=False)

@api.model
def create(self, vals):
    if vals.get("name", "New") == "New":
        vals["name"] = self.env["ir.sequence"].next_by_code("clinic.appointment") or "New"
    return super().create(vals)
```
Teacher demonstrated this pattern for auto-generating reference numbers.

## Security — Critical Distinction Teacher Made:
"In security CSV, you use the TABLE NAME (from _name), NOT the file name."
"The only place where the FILE NAME matters is in __init__.py imports."
"These two are completely different things and confusing them causes errors."

## Debugging — Teacher's Most Repeated Advice:
1. "Always upgrade the module first — it tells you EXACTLY the file and line."
2. "Check your init.py — did you import the new model?"
3. "Check your security CSV — did you add the new model?"
4. "Check your manifest — is the XML file listed? In the right order?"
5. "Spelling mistakes are the #1 cause of errors — missing slash, extra space."
6. "If table doesn't update and XML fails: comment out the XML change, restart, 
   uncomment, restart again. Sometimes model and XML can't update simultaneously."
7. "Indentation in Python is CRITICAL. Wrong indent = function not part of class = 
   it won't run."
8. "XML is very sensitive about opening and closing tags. A missing </group> breaks everything."

===============================================================================
SESSION 4 TEACHINGS
===============================================================================

## Constraints — Two Types, Teacher's Exact Teaching:

### SQL Constraints (stop record from being created at all):
```python
_sql_constraints = [
    ('check_expected_price', 'CHECK(expected_price > 0)', 
     'The expected price must be positive.'),
    ('check_selling_price', 'CHECK(selling_price > 0)', 
     'The selling price must be positive.'),
    ('unique_type_name', 'UNIQUE(name)', 
     'A property type must be unique.'),
]
```
Teacher: "SQL constraint = the database itself refuses to add the record."
Teacher: "Use for: price > 0, uniqueness checks — things that should NEVER be in the DB."

### Python Constraints (business logic validation):
```python
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import ValidationError

@api.constrains("selling_price", "expected_price")
def _check_valid_selling_price(self):
    for record in self:
        if (float_compare(record.selling_price, 0.9 * record.expected_price, 
                         precision_digits=2) < 0
                and not float_is_zero(record.selling_price, precision_digits=2)):
            raise ValidationError("Selling price cannot be lower than 90% of expected price.")
```
Teacher: "Python constraint = business logic. Use ValidationError, not UserError."
Teacher on float_compare: "Don't use regular == or < for floats — rounding errors in 
Python mean 3.00001 might not equal 3.00002. Use float_compare and float_is_zero."
Teacher: "float_compare returns -1, 0, or 1. Less than zero means value1 < value2."
Teacher: "precision_digits=2 means round to 2 decimal places."

## Many2many Tags Widget — Teacher's Teaching:
```xml
<field name="tag_ids" widget="many2many_tags"/>
```
Teacher: "Without the widget it shows as a list with 'Add a line' — ugly. 
With many2many_tags widget it shows as colored pills — much better UI."
Teacher: "This widget ONLY works for many2many relationships."

## Kanban View — Teacher's Pattern:
```xml
<kanban default_group_by="property_type_id" records_draggable="False">
    <templates>
        <t t-name="kanban-card">
            <field name="name"/>
            <field name="expected_price"/>
            <field name="tag_ids" widget="many2many_tags"/>
        </t>
    </templates>
</kanban>
```
In manifest action:
```xml
<field name="view_mode">list,form,kanban</field>
```
Teacher: "Kanban is drag-and-drop cards grouped by a field. default_group_by sets 
what it groups by on load. records_draggable=False means you can't drag between groups."

## Invisible Attribute for Garden Logic:
```xml
<field name="garden_area" invisible="not has_garden"/>
```
Teacher: "This is what someone asked about session 1 — hide garden_area if has_garden 
is False. It's just: invisible='not has_garden'. That simple."

## Project Structure for Hackathon — Teacher's Exact Advice:
Teacher: "You don't need a new database. Create a new folder inside workshop/ with 
the same file structure as estate. Change launch.json to point to your new module name.
Estate stays there — it won't be deleted. Your new module just gets created alongside it."
Teacher: "Follow the SAME workflow we learned. Same file structure. Same patterns."

## State Machine Pattern — Teacher's Complete Flow:
Property states: new → offer_received → offer_accepted → sold
                                                        ↘ cancelled (from any state)

How each transition is triggered:
- new → offer_received: override create() in offers model
- offer_received → offer_accepted: in accept_offer() function
- any → sold: sell_property() button function
- any → cancelled: cancel_property() button function

Teacher: "We're not trying to move back from offer_accepted to offer_received. 
In real life bidding closes, you evaluate, you sell. That's the flow."

===============================================================================
CRITICAL PATTERNS — Teacher's Most Emphasized Points
===============================================================================

1. FILE NAME vs TABLE NAME are different things
   - File: estate_property_offers.py
   - Table (_name): "estate.property.offer" 
   - init.py uses: FILE name
   - security CSV uses: TABLE name  
   - XML uses: TABLE name
   - "This caused SO many bugs. They are NOT the same."

2. ALWAYS restart server after code changes
   Teacher: "Server does not pick up changes automatically."

3. ALWAYS add new models to THREE places:
   - models/__init__.py (import)
   - security/ir.model.access.csv (permissions)
   - __manifest__.py (only for XML files, not Python)

4. for record in self IS MANDATORY in all methods
   Teacher: "Even if you think it's one record, always loop."

5. Manifest load order matters
   security → views → menus
   "Wrong order = errors guaranteed."

6. XML closing tags — teacher's most common bug fix
   "Missing </group> </page> </notebook> breaks everything downstream."

7. UPGRADE MODULE to debug — teacher said this 20+ times
   "Apps → your module → three dots → Upgrade. Tells you exactly what's wrong."

8. Computed fields need store=True if you want to filter/search on them
   Teacher demonstrated this pattern throughout.

9. super().create() must RETURN the record
   "return super().create(vals)" — the return is mandatory.

10. Default for lambda:
    default=lambda self: self.env.user
    Teacher: "self.env = Odoo environment. self.env.user = current logged-in user."

===============================================================================
WHAT THE TEACHER EXPLICITLY SAID NOT TO DO
===============================================================================

- Don't create a separate table for clients — use res.partner
- Don't create a separate table for employees/salespersons — use res.users  
- Don't use regular Python comparison for floats — use float_compare
- Don't skip the for loop in methods even for single records
- Don't add 'cancelled' to statusbar_visible (statusbar = progression, not all states)
- Don't update XML and model simultaneously if having issues — do model first, verify, then XML
- Don't use JavaScript in Odoo frontend — XML widgets handle styling

===============================================================================
TEACHER'S EVALUATION CRITERIA (from Session 4 announcements)
===============================================================================

Code evaluation looks for:
1. General formal workflow
2. Comments in code
3. GitHub hosting with setup instructions
4. Extra points for live deployment (optional)
"We won't be looking too deep — we want a general formal workflow."

Grading: 30% workshops + 70% hackathon (40% pitch + 30% code evaluation)
