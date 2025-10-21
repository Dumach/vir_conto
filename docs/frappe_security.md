# How to make Frappe Framework more secure in Production

## 1. Disable Administrator Login:

With an app called "block_administrator", we can opt out the login possibility for the Administrator user.

This makes our website harder to bruteforce by:
 - Eliminates High-Value Targets: Removes the most privileged account from direct attack surface
 - Reduces Attack Success Rate: Forces attackers to target less obvious accounts
 - Prevents Credential Stuffing: Blocks automated login attempts using common passwords
 - Maintains System Integrity: All background operations continue normally

Source:
https://immanuelraj.dev/secure-frappe-admin-block-administrator-guide/


## 2. Disable Error Traceback in Frappe:

The Problem:
Default settings can expose detailed backend exceptions on the frontend after an error, like a failed login.

The Impact:
This isn't just messy; it's a security risk. These tracebacks can reveal server file paths, software versions, and database details. For an attacker, this information is a goldmine for planning a targeted attack.

The Solution:
A single checkbox in System Settings called `allow_error_traceback`.

Source:
https://www.linkedin.com/posts/rammd_frappe-erpnext-cybersecurity-activity-7372691964242165760-Di2g


# +1 All the known vulnerabilities found in Frappe (v15.57)

https://csirt.sk/frappe-framework-vulnerabilities.html




