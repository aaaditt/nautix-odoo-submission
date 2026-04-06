# this manifest defines the nautix module's metadata and dependencies
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
    ],
    "assets": {
        "web.assets_backend": [
            "nautix/static/src/components/ai_dashboard/ai_dashboard.xml",
            "nautix/static/src/components/ai_dashboard/ai_dashboard.js",
            "nautix/static/src/components/ai_dashboard/ai_dashboard.scss",
        ]
    }
}
