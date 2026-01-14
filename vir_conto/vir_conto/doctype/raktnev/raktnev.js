// Copyright (c) 2025, Alex Nagy and contributors
// For license information, please see license.txt

frappe.ui.form.on("raktnev", {
  refresh(frm) {
    frm.add_custom_button(__("Repair raktnev in vir_bolt"), () => {
      frappe.confirm(
        __("Are you sure you want to proceed?"),
        () => {
          // Yes
          frm.call({
            doc: frm.doc,
            method: "update_raktnev",
            callback: function (r) {
              frappe.msgprint(r.message);
            },
            error: (r) => {
              // on error
              frappe.msgprint(r.message);
            },
          });
        },
        () => {
          // No
        },
      );
    });
  },
});
