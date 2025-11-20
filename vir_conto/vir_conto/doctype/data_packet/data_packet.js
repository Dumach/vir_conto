frappe.ui.form.on("Data Packet", {
  refresh(frm) {
    frm.add_custom_button(__("Import Data"), function () {
      frappe.call({
        // Call as a *document method*:
        doc: frm.doc,
        method: "import_packet",
        freeze: true,
        freeze_message: __("Importing data..."),
        callback: function (r) {
          if (!r.exc) {
            frappe.msgprint(__("Import completed successfully."));
            frm.reload_doc();
          }
        },
      });
    });
  },
});
