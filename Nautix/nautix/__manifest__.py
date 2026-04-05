{
    "name": "Nautix — Ship Chartering",
    "version": "19.0.1.0.0",
    "author": "Aadit",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account"],
    "application": True,
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "data/sequences.xml",
        "report/charter_party_report.xml",
        "views/views.xml",
        "data/demo_data.xml",
    ]
}
