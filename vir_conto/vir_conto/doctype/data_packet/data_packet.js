frappe.ui.form.on("Data Packet", {
  refresh(frm) {
    frm.add_custom_button(__("Import Data"), () => {
      frappe.call({
        // Call as a *document method*:
        doc: frm.doc,
        method: "import_packet",
        args: { verbose: "web" },
        // freeze: true,
        // freeze_message: __("Importing data..."),
        callback: (r) => {
          if (!r.exc) {
            if (cur_dialog) cur_dialog.hide();
            frappe.msgprint(__("Import completed successfully."));
            frm.reload_doc();
          }
        },
        error: (r) => {
          // on error
          frappe.msgprint(r.message);
        },
      });
    });

    frm.add_custom_button(__("Go to File"), () => {
      frappe.db
        .get_doc("File", null, { file_name: frm.doc.name })
        .then((doc) => {
          frappe.set_route("file", doc.name);
        });
    });
  },
});
